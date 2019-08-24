
#include "src/XInput/XInput.h"

#include "data.cpp"

#define OUTPUT_EMPTY 0
#define OUTPUT_TERMINATE 1
#define OUTPUT_LEFT 2
#define OUTPUT_RIGHT 3
#define OUTPUT_UP 4
#define OUTPUT_DOWN 5
#define OUTPUT_ZL 6
#define OUTPUT_ZR 7
#define OUTPUT_A 8

#define PRESS_DELAY 35

#define JOYSTICK_MAX 2
#define JOYSTICK_NEUTRAL 1

size_t next_value_index = 0;
uint32_t load_value() {
  return COMMAND_DATA[next_value_index++];
}

uint32_t cur_value = 0;
int cur_value_bit_count = 0;
int next_bit() {
  if (cur_value_bit_count == 0) {
    cur_value_bit_count = 32;
    cur_value = load_value();
  }
  cur_value_bit_count--;
  int bit = (int)((cur_value >> cur_value_bit_count) & 1);
  return bit;
}

uint16_t state = 0;
boolean is_a_held = false;

void do_output(char c) {
  switch (c) {
      case 'L':
        XInput.setDpad(0, 0, 1, 0);
        break;
      case 'R':
        XInput.setDpad(0, 0, 0, 1);
        break;
      case 'U':
        XInput.setDpad(1, 0, 0, 0);
        break;
      case 'D':
        XInput.setDpad(0, 1, 0, 0);
        break;
      case '<':
        XInput.setTrigger(TRIGGER_LEFT, JOYSTICK_MAX);
        break;
      case '>':
        XInput.setTrigger(TRIGGER_RIGHT, JOYSTICK_MAX);
        break;
      case '{':
        XInput.press(BUTTON_LB);
        break;
      case '}':
        XInput.press(BUTTON_RB);
        break;
      case 'A':
        XInput.press(BUTTON_B);
        break;
      case '.':
        delay(PRESS_DELAY);
        if (!is_a_held) XInput.release(BUTTON_B);
        XInput.release(BUTTON_LB);
        XInput.release(BUTTON_RB);
        XInput.setTrigger(TRIGGER_LEFT, 0);
        XInput.setTrigger(TRIGGER_RIGHT, 0);
        XInput.setDpad(0, 0, 0, 0);
        delay(PRESS_DELAY);
        break;
      case '+':
        is_a_held = !is_a_held;
        if (is_a_held) {
          XInput.press(BUTTON_B);
        } else {
          XInput.release(BUTTON_B);
        }
        break;
        
  }
}

void setup() {
  XInput.begin();
  XInput.setJoystickRange(0, JOYSTICK_MAX);
  XInput.setTriggerRange(0, JOYSTICK_MAX);

  delay(1000);
  
  while (true) {
    int bit = next_bit();
    TransitionItem item = TRANSITION_TABLE[state][bit];

    for (size_t i = 0; item.output[i]; i++) {
      char c = item.output[i];
      if (c == '#') return;
      do_output(c);
    }
    
    state = item.next_state;
  }
}

void loop() { }
