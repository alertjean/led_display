
    /********** ACCURATE TIMER for REAL TIME CONTROL ***

    This C program illustrates accurate timing on a
    Raspberry Pi by sending a 50kHz signal to a GPIO pin
    with a jitter of about 0.1 microseconds. It uses the
    processor's 1MHz timer and disables interrupts.
    It includes GPIO setup and read/write code.

    Compiled from console with gcc under the standard
    Debian distribution.
    Tested with a keyboard and HDMI monitor attached,
    and X Windows not started.

    **************************************************/


    /*********** TIMER CODE example *******

    unsigned int timend;

    setup()                  // initialise system
                             // call only once

    interrupts(0);           // disable interrupts

    timend = *timer + 200;   // Set up 200 microsecond delay
                             // Maximum possible delay
                             // is 7FFFFFF or about 35 minutes

    while((((*timer)-timend) & 0x80000000) != 0);  // delay loop

                         // This works even if *timer
                         // overflows to zero during the delay,
                         // or if the while test misses the exact
                         // termination when (*timer-timend) == 0.
                         // Jitter in delay about 1 microsceond.
                         // Can be reduced to about 0.1 microsecond
                         // by synchronising the timend set
                         // instruction to a change in *timer

                         // if interrupts are not disabled
                         // the delay can occasionally be
                         // 2ms (or more) longer than requested
                         // and is routinely out by up to 0.1ms

    interrupts(1);       // re-enable interrupts

    *************************************************/

    #include <stdio.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <sys/mman.h>

    #define GPIO_BASE  0x20200000
    #define TIMER_BASE 0x20003000
    #define INT_BASE 0x2000B000

    volatile unsigned *gpio,*gpset,*gpclr,*gpin,*timer,*intrupt;

    /******************** GPIO read/write *******************/
      // outputs  CLK = GPIO 15 = connector pin 10
      //          DAT = GPIO 14 = connector pin 8
      // code example
      //    CLKHI;
    #define CLKHI *gpset = (1 << 15)  // GPIO 15
    #define CLKLO *gpclr = (1 << 15)
    #define DATHI *gpset = (1 << 14)  // GPIO 14
    #define DATLO *gpclr = (1 << 14)
      // inputs   P3  = GPIO 3 = connector pin 5 (Rev 2 board)
      //          P2  = GPIO 2 = connector pin 3 (Rev 2 board)
      //          ESC = GPIO 18 = connector pin 12
      // code examples
      //   if(P2IN == 0)
      //   if(P2IN != 0)
      //   n = P2INBIT;  //  0 or 1
    #define ESCIN (*gpin & (1 << 18))   // GPIO 18
    #define P2IN (*gpin & (1 << 2))    // GPIO 2
    #define P3IN (*gpin & (1 << 3)     // GPIO 3
    #define P2INBIT ((*gpin >> 2) & 1)  // GPIO 2
    #define P3INBIT ((*gpin >> 3) & 1)  // GPIO 3
    /******************* END GPIO ****************/

    int setup(void);
    int interrupts(int flag);

    main()
      {
      int n,getout;
      unsigned int timend;

      sleep(1);    // 1 second delay
                   // When the program starts, the interrupt
                   // system may still be dealing with the
                   // last Enter keystroke. This gives it
                   // time to finish.

      setup();     // setup GPIO, timer and interrupt pointers

      interrupts(0);    // Disable interrupts to ensure
                        // accurate timing.
                        // Re-enable via interrupts(1) as
                        // soon as accurate timing is no
                        // longer needed.

            // screen output, keyboard input (and who
            // knows what else) stop working until
            // interrupts are re-enabled

      // 50kHz signal to CLK output = GPIO 15 connector pin 10
      // 1000000 cycles = 20 seconds
      // checks ESC input pin = GPIO 18 connector pin 12
      // if lo - loop terminates

      getout = 0;
      timend = *timer + 10;   // set up 10us delay from
                              // current timer value
      for(n = 0 ;  n < 1000000 && getout == 0 ; ++n)
        {
                              //  delay to timend
        while( (((*timer)-timend) & 0x80000000) != 0);

        CLKHI;           // output GPIO 15 hi

                         // check input GPIO 18 pin
                         // which is pulled hi by setup()
                         // exit loop if lo
        if(ESCIN == 0)
          getout = 1;
                             // 10us delay
        timend += 10;
        while( (((*timer)-timend) & 0x80000000) != 0);

        CLKLO;               // output GPIO 15 lo

        timend += 10;        // 10us delay at start of next loop
        }

      interrupts(1);         // re-enable interrupts

      return;
      }

    /******************** INTERRUPTS *************

    Is this safe?
    Dunno, but it works

    interrupts(0)   disable interrupts
    interrupts(1)   re-enable interrupts

    return 1 = OK
           0 = error with message print

    Uses intrupt pointer set by setup()
    Does not disable FIQ which seems to
    cause a system crash
    Avoid calling immediately after keyboard input
    or key strokes will not be dealt with properly

    *******************************************/

    int interrupts(int flag)
      {
      static unsigned int sav132 = 0;
      static unsigned int sav133 = 0;
      static unsigned int sav134 = 0;

      if(flag == 0)    // disable
        {
        if(sav132 != 0)
          {
          // Interrupts already disabled so avoid printf
          return(0);
          }

        if( (*(intrupt+128) | *(intrupt+129) | *(intrupt+130)) != 0)
          {
          printf("Pending interrupts\n");  // may be OK but probably
          return(0);                       // better to wait for the
          }                                // pending interrupts to
                                           // clear

        sav134 = *(intrupt+134);
        *(intrupt+137) = sav134;
        sav132 = *(intrupt+132);  // save current interrupts
        *(intrupt+135) = sav132;  // disable active interrupts
        sav133 = *(intrupt+133);
        *(intrupt+136) = sav133;
        }
      else            // flag = 1 enable
        {
        if(sav132 == 0)
          {
          printf("Interrupts not disabled\n");
          return(0);
          }

        *(intrupt+132) = sav132;    // restore saved interrupts
        *(intrupt+133) = sav133;
        *(intrupt+134) = sav134;
        sav132 = 0;                 // indicates interrupts enabled
        }
      return(1);
      }

    /***************** SETUP ****************
    Sets up five GPIO pins as described in comments
    Sets timer and interrupt pointers for future use
    Does not disable interrupts
    return 1 = OK
           0 = error with message print
    ************************************/

    int setup()
      {
      int memfd;
      unsigned int timend;
      void *gpio_map,*timer_map,*int_map;

      memfd = open("/dev/mem",O_RDWR|O_SYNC);
      if(memfd < 0)
        {
        printf("Mem open error\n");
        return(0);
        }

      gpio_map = mmap(NULL,4096,PROT_READ|PROT_WRITE,
                      MAP_SHARED,memfd,GPIO_BASE);

      timer_map = mmap(NULL,4096,PROT_READ|PROT_WRITE,
                      MAP_SHARED,memfd,TIMER_BASE);

      int_map = mmap(NULL,4096,PROT_READ|PROT_WRITE,
                      MAP_SHARED,memfd,INT_BASE);

      close(memfd);

      if(gpio_map == MAP_FAILED ||
         timer_map == MAP_FAILED ||
         int_map == MAP_FAILED)
        {
        printf("Map failed\n");
        return(0);
        }
                  // interrupt pointer
      intrupt = (volatile unsigned *)int_map;
                  // timer pointer
      timer = (volatile unsigned *)timer_map;
      ++timer;    // timer lo 4 bytes
                  // timer hi 4 bytes available via *(timer+1)

                  // GPIO pointers
      gpio = (volatile unsigned *)gpio_map;
      gpset = gpio + 7;     // set bit register offset 28
      gpclr = gpio + 10;    // clr bit register
      gpin = gpio + 13;     // read all bits register

          // setup  GPIO 2/3 = inputs    have pull ups on board
          //        control reg = gpio + 0 = pin/10
          //        GPIO 2 shift 3 bits by 6 = (pin rem 10) * 3
          //        GPIO 3 shift 3 bits by 9 = (pin rem 10) * 3

      *gpio &= ~(7 << 6);   // GPIO 2  3 bits = 000 input
      *gpio &= ~(7 << 9);   // GPIO 3  3 bits = 000 input

         // setup GPIO 18 = input
      *(gpio+1) &= ~(7 << 24);  // GPIO 18 input
         // enable pull up on GPIO 18
      *(gpio+37) = 2;           // PUD = 2  pull up
                                //     = 0  disable pull up/down
                                //     = 1  pull down
      timend = *timer+2;        // 2us delay
      while( (((*timer)-timend) & 0x80000000) != 0);
      *(gpio+38) = (1 << 18);   // PUDCLK bit set clocks PUD=2 to GPIO 18
      timend = *timer+2;        // 2us delay
      while( (((*timer)-timend) & 0x80000000) != 0);
      *(gpio+37) = 0;           // zero PUD
      *(gpio+38) = 0;           // zero PUDCLK
                                // finished pull up enable

         //      GPIO 14/15 = outputs
         //      control reg = gpio + 1 = pin/10
         //      GPIO 14 shift 3 bits by 12 = (pin rem 10) * 3
         //      GPIO 15 shift 3 bits by 15 = (pin rem 10) * 3

      *(gpio+1) &= ~(7 << 12);  // GPIO 14 zero 3 bits
      *(gpio+1) |= (1 << 12);   // 3 bits = 001 output

      *(gpio+1) &= ~(7 << 15);  // GPIO 15 zero 3 bits
      *(gpio+1) |= (1 << 15);   // 3 bits = 001 output

      return(1);
      }

    /**************** PULL UPS *********

    pull up register  PUD = gpio+37
    clock register PUDCLK = gpio+38

    1. set PUD =  0 disable pull up/down
                  1 enable pull down
                  2 enable pull up
                  3 reserved
       *(gpio+37) = 2  to pull up

    2. wait 150 cycles

    3. set bit of GPIO pin in PUDCLK
       so for GPIO 3    *(gpio+38) = 8
       to clock PUD into GPIO 3 only

    4. wait 150 cycles

    5. write 0 to PUD

    6. write 0 to PUDCLK

    ************ END ************************/


