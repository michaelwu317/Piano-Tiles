#include <stdio.h>
#include "board.h"
#include "peripherals.h"
#include "pin_mux.h"
#include "clock_config.h"
#include "MKL46Z4.h"
#include "fsl_debug_console.h"
#include "fsl_uart.h"
#include "utils.h"
int SWITCH_1_PIN = 3;
int SWITCH_3_PIN = 12;
int ontimeleft = 0;
int ontimeright = 0;

// printf to UART must be enabled in the project!
int main(void) {

    /* Init board hardware. */
    BOARD_InitBootPins();
    BOARD_InitBootClocks();
    /* Init FSL debug console. */
  	BOARD_InitDebugConsole();

	LED_Initialize();
	LED_Off();
	SWITCH1_Initialize();

	NVIC_EnableIRQ(UART0_IRQn);
	NVIC_EnableIRQ(PORTC_PORTD_IRQn);
	UART_EnableInterrupts(UART0,kUART_RxActiveEdgeInterruptEnable);
	UART_EnableRx(UART0, 1);

	printf("BOOT\r\n");

	while (1) {
		if (ontimeright) {
			LEDGreen_On();
			for(int j=0; j<500000; j++) {
				if (!ontimeright) break;
			}
			LED_Off();
			if (ontimeright) {
				printf("MISSEDRIGHT\r\n");
			}
			ontimeright = 0;
		}
		if (ontimeleft) {
			LEDRed_On();
			for(int j=0; j<500000; j++) {
				if (!ontimeleft) break;
			}
			LED_Off();
			if (ontimeleft) {
				printf("MISSEDLEFT\r\n");
			}
			ontimeleft = 0;
		}
	}
}

void UART0_IRQHandler(void) {
	char str[10];
	scanf("%s", str);
	if (strcmp(str,"RIGHT") == 0) {
		ontimeright = 1;
	} else if (strcmp(str,"LEFT") == 0) {
		ontimeleft = 1;
	}
	printf( "[DEBUG] You entered: %s\r\n", str);
	UART_ClearStatusFlags(UART0, kUART_RxActiveEdgeFlag);
}

void PORTC_PORTD_IRQHandler(void) {
	if (PORTC->PCR[SWITCH_1_PIN] & (1 << 24)) {
		printf("RIGHT\r\n");
		if (ontimeright) {
			ontimeright = 0;
			LEDRed_On(); // SW1 (right) button pressed, toggle LED
			printf("ONTIMERIGHT\r\n");
			delayshort();
			LED_Off();
		} else {
			printf("BADPRESS\r\n");
		}
		PORTC->PCR[SWITCH_1_PIN] |= PORT_PCR_ISF(1);  // clear the interrupt status flag by writing 1 to it
	} else {
		printf("LEFT\r\n");
		if (ontimeleft) {
			ontimeleft = 0;
			LEDGreen_On(); // SW1 (right) button pressed, toggle LED
			printf("ONTIMELEFT\r\n");
			delayshort();
			LED_Off();
		} else {
			printf("BADPRESS\r\n");
		}
		PORTC->PCR[SWITCH_3_PIN] |= PORT_PCR_ISF(1);  // clear the interrupt status flag by writing 1 to it
	}
}
