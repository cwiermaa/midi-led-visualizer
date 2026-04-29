import argparse
import json
import math
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mido
import serial


@dataclass
class KeyState:
    key_index: int
    midi_note: int
    is_down: bool = False
    color: tuple[int, int, int] = (0, 0, 0)


class MidiLedVisualizer:
    def __init__(self, config: dict):
        self.config = config

        self.midi_queue: queue.Queue[mido.Message] = queue.Queue()

        self.lowest_midi_note: int = config.get("lowest_midi_note", 21)
        self.num_keys: int = config.get("num_keys", 88)
        self.led_offset: int = config.get("led_offset", 0)

        self.sustain_cc: int = config.get("sustain_cc", 64)
        self.sostenuto_cc: int = config.get("sostenuto_cc", 66)

        self.frame_rate: int = config.get("frame_rate", 60)
        self.period: float = 1.0 / self.frame_rate

        self.sustain_on: bool = False
        self.sostenuto_was_down: bool = False

        self.color_maps: list[dict] = config.get("color_maps", [])
        if not self.color_maps:
            raise ValueError("config must contain at least one color map")

        self.color_map_index: int = 0

        self.key_states = [
            KeyState(
                key_index=i,
                midi_note=self.lowest_midi_note + i,
            )
            for i in range(self.num_keys)
        ]

        self.serial_connection: Optional[serial.Serial] = None

    # ---------- Device listing ----------

    @staticmethod
    def list_midi_devices() -> None:
        print("MIDI input devices:")
        for name in mido.get_input_names():
            print(f"  IN : {name}")

        print("\nMIDI output devices:")
        for name in mido.get_output_names():
            print(f"  OUT: {name}")

    # ---------- MIDI ----------

    def start_midi_thread(self) -> None:
        input_name = self.config.get("midi_input_name")
        output_name = self.config.get("midi_output_name")
        forwarding_enabled = self.config.get("enable_midi_forwarding", False)

        if not input_name:
            raise ValueError("config must define midi_input_name")

        thread = threading.Thread(
            target=self._midi_listener,
            args=(input_name, output_name, forwarding_enabled),
            daemon=True,
        )
        thread.start()

    def _midi_listener(
        self,
        input_name: str,
        output_name: Optional[str],
        forwarding_enabled: bool,
    ) -> None:
        print(f"Opening MIDI input: {input_name}")

        if forwarding_enabled:
            if not output_name:
                raise ValueError(
                    "enable_midi_forwarding is true, but midi_output_name is not set"
                )

            print(f"Forwarding MIDI to: {output_name}")

            with mido.open_input(input_name) as inport, mido.open_output(output_name) as outport:
                for msg in inport:
                    self.midi_queue.put(msg)
                    outport.send(msg)
        else:
            with mido.open_input(input_name) as inport:
                for msg in inport:
                    self.midi_queue.put(msg)

    # ---------- Serial / Arduino ----------

    def connect_serial(self) -> None:
        port = self.config.get("serial_port")
        baud_rate = self.config.get("baud_rate", 115200)

        if not port:
            raise ValueError("config must define serial_port")

        print(f"Opening serial port: {port} @ {baud_rate}")
        self.serial_connection = serial.Serial(port, baud_rate, timeout=1)

        # Give Arduino time to reset after serial connection opens.
        time.sleep(2)

        print("Waiting for Arduino READY...")
        while True:
            line = self.serial_connection.readline().decode(errors="ignore").strip()
            if line == "READY":
                print("Arduino ready.")
                return

    def send_led_frame(self) -> None:
        if self.serial_connection is None:
            raise RuntimeError("Serial connection is not open")

        active_states = [
            state
            for state in self.key_states
            if state.color != (0, 0, 0)
        ]

        if active_states:
            payload = b"".join(
                bytes(
                    [
                        self._clamp_byte(state.key_index + self.led_offset),
                        self._clamp_byte(state.color[0]),
                        self._clamp_byte(state.color[1]),
                        self._clamp_byte(state.color[2]),
                    ]
                )
                for state in active_states
            )
        else:
            # Send a harmless out-of-range LED index to indicate "no active LEDs".
            # The Arduino clears the strip every frame before applying chunks.
            payload = bytes([255, 0, 0, 0])

        self.serial_connection.reset_input_buffer()
        self.serial_connection.write(payload)

        while True:
            response = self.serial_connection.readline().decode(errors="ignore").strip()
            if response == "DONE":
                break

    # ---------- Color maps ----------

    def current_color_map(self) -> dict:
        return self.color_maps[self.color_map_index]

    def cycle_color_map(self) -> None:
        self.color_map_index = (self.color_map_index + 1) % len(self.color_maps)
        color_map = self.current_color_map()
        print(f"Color map: {color_map.get('name', self.color_map_index)}")

        # Optional behavior: clear currently held colors when switching modes.
        # Comment this out if you want currently-held notes to keep old colors.
        for state in self.key_states:
            if state.is_down:
                state.color = self.color_for_key(state.key_index)

    def color_for_key(self, key_index: int) -> tuple[int, int, int]:
        color_map = self.current_color_map()
        default = tuple(color_map.get("default", [0, 0, 0]))

        for rule in color_map.get("ranges", []):
            if rule["from"] <= key_index <= rule["to"]:
                return tuple(rule["color"])

        return default

    # ---------- Main state updates ----------

    def process_midi_messages(self) -> None:
        while not self.midi_queue.empty():
            msg = self.midi_queue.get()

            if msg.type == "note_on":
                # MIDI convention: note_on velocity 0 is equivalent to note_off.
                if getattr(msg, "velocity", 0) == 0:
                    self.handle_note_off(msg.note)
                else:
                    self.handle_note_on(msg.note)

            elif msg.type == "note_off":
                self.handle_note_off(msg.note)

            elif msg.type == "control_change":
                self.handle_control_change(msg.control, msg.value)

    def handle_note_on(self, midi_note: int) -> None:
        key_index = midi_note - self.lowest_midi_note

        if not 0 <= key_index < self.num_keys:
            return

        state = self.key_states[key_index]
        state.is_down = True
        state.color = self.color_for_key(key_index)

    def handle_note_off(self, midi_note: int) -> None:
        key_index = midi_note - self.lowest_midi_note

        if not 0 <= key_index < self.num_keys:
            return

        state = self.key_states[key_index]
        state.is_down = False

        if not self.sustain_on:
            state.color = (0, 0, 0)

    def handle_control_change(self, control: int, value: int) -> None:
        is_down = value > 0

        if control == self.sustain_cc:
            self.sustain_on = is_down

            if not self.sustain_on:
                self.clear_released_keys()

        elif control == self.sostenuto_cc:
            # Cycle once on pedal-down, not repeatedly while held.
            if is_down and not self.sostenuto_was_down:
                self.cycle_color_map()

            self.sostenuto_was_down = is_down

    def clear_released_keys(self) -> None:
        for state in self.key_states:
            if not state.is_down:
                state.color = (0, 0, 0)

    # ---------- Run loop ----------

    def run(self) -> None:
        self.start_midi_thread()
        self.connect_serial()

        print(f"Starting loop at {self.frame_rate} FPS")
        print(f"Color map: {self.current_color_map().get('name', self.color_map_index)}")

        try:
            while True:
                start = time.time()

                self.process_midi_messages()
                self.send_led_frame()

                elapsed = time.time() - start
                time.sleep(max(0, self.period - elapsed))

        except KeyboardInterrupt:
            print("\nExiting on Ctrl+C.")

        finally:
            if self.serial_connection is not None:
                self.serial_connection.close()
                print("Serial connection closed.")

    @staticmethod
    def _clamp_byte(value: int) -> int:
        return max(0, min(255, int(math.floor(value))))


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MIDI-driven LED visualizer for piano/keyboard input."
    )

    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config JSON file. Default: config.json",
    )

    parser.add_argument(
        "--list-midi",
        action="store_true",
        help="List available MIDI input/output devices and exit.",
    )

    args = parser.parse_args()

    if args.list_midi:
        MidiLedVisualizer.list_midi_devices()
        return

    config = load_config(Path(args.config))
    app = MidiLedVisualizer(config)
    app.run()


if __name__ == "__main__":
    main()