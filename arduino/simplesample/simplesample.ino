//simplesample.ino

const int PIN_LED = 13;
const int PIN_SAMPLE = 7; // Port D bit 7

const int ADC_CHANNEL = 0;
const int CPU_FREQ = 16000000;

void setup() {
  // put your setup code here, to run once:
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_SAMPLE, OUTPUT);

  // Configure timer 1 to trigger at 9600Hz
	/* Set prescaler to clk/8 (2 MHz), CTC, top = ICR1 */
	TCCR1A = 0;
	TCCR1B = bit(CS11) | bit(WGM13) | bit(WGM12);
	/* Set max value to obtain a 9600Hz freq */
	ICR1 = ((CPU_FREQ / 8) / 9600) - 1;

	/* Set reference to AVCC (5V), select channel */
	ADMUX = bit(REFS0) | ADC_CHANNEL;

	DDRC &= ~bit(ADC_CHANNEL);
	PORTC &= ~bit(ADC_CHANNEL);

	// Disable digital input on ADC channel
	DIDR0 |= bit(ADC_CHANNEL);


  /* Set ADC autotrigger on Timer1 Input capture flag */
	ADCSRB = bit(ADTS2) | bit(ADTS1) | bit(ADTS0);

	/* Enable ADC, autotrigger, 1MHz, IRQ enabled */
	/* We are using the ADC a bit out of specifications otherwise it's not fast enough for our
	 * purposes */
	ADCSRA = bit(ADEN) | bit(ADSC) | bit(ADATE) | bit(ADIE) | bit(ADPS2);

	digitalWrite(PIN_LED, HIGH);
	PORTD |= bit(7);
}

void loop() {

}



ISR(ADC_vect)
{
	// Clear the Input Capture Flag by writing 1 to it.
	TIFR1 = bit(ICF1) | bit(OCF1B);

	// DEBUG: turn on pin 13 LED
	PORTB |= bit(5);
  PORTD |= bit(7);

  // Get the scaled input value
	int8_t sample = (ADCW) >> 2 - 128;

	// Turn LED on if > 0 
	//if (sample > 0) {
//		PORTD |= bit(7);
//	}
//	else { 
//		PORTD &= ~bit(7);
//	}

	// DEBUG: turn off pin 13 LED
	PORTB &= ~bit(5);
	PORTD &= ~bit(7);
}