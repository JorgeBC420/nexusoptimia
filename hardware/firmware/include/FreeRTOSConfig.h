/*
 * NexusOptim IA - FreeRTOS Configuration
 * Optimized for CH32V003 RISC-V (20KB Flash, 2KB RAM)
 * 
 * Copyright (c) 2025 OpenNexus
 * Licensed under MIT License
 */

#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

/* RISC-V Architecture Settings */
#define configCPU_CLOCK_HZ                      48000000    // 48MHz system clock
#define configTICK_RATE_HZ                      1000        // 1ms tick period
#define configUSE_PREEMPTION                    1           // Enable preemptive scheduling
#define configUSE_TIME_SLICING                  1           // Enable time slicing
#define configUSE_PORT_OPTIMISED_TASK_SELECTION 0           // Standard task selection
#define configUSE_TICKLESS_IDLE                 1           // Enable tickless idle for power saving

/* Memory Management - Optimized for 2KB RAM */
#define configTOTAL_HEAP_SIZE                   1024        // 1KB heap (50% of RAM)
#define configMINIMAL_STACK_SIZE                64          // 64 words minimum stack
#define configMAX_TASK_NAME_LEN                 8           // Short task names
#define configUSE_16_BIT_TICKS                  1           // Use 16-bit tick counter

/* Task Configuration */
#define configMAX_PRIORITIES                    4           // 4 priority levels (0-3)
#define configIDLE_SHOULD_YIELD                 1           // Idle task yields
#define configUSE_TASK_NOTIFICATIONS            1           // Enable task notifications
#define configTASK_NOTIFICATION_ARRAY_ENTRIES   1           // Single notification per task

/* Kernel Features - Minimal for memory optimization */
#define configUSE_MUTEXES                       1           // Enable mutexes
#define configUSE_RECURSIVE_MUTEXES             0           // Disable recursive mutexes
#define configUSE_COUNTING_SEMAPHORES           0           // Disable counting semaphores
#define configUSE_QUEUE_SETS                    0           // Disable queue sets
#define configQUEUE_REGISTRY_SIZE               0           // No queue registry

/* Software Timers - Disabled to save memory */
#define configUSE_TIMERS                        0
#define configTIMER_TASK_PRIORITY               0
#define configTIMER_QUEUE_LENGTH                0
#define configTIMER_TASK_STACK_DEPTH            0

/* Event Groups - Disabled to save memory */
#define configUSE_EVENT_GROUPS                  0

/* Stream Buffers - Disabled to save memory */
#define configUSE_STREAM_BUFFERS                0

/* Co-routines - Disabled */
#define configUSE_CO_ROUTINES                   0
#define configMAX_CO_ROUTINE_PRIORITIES         0

/* Debug and Statistics - Disabled for production */
#define configUSE_TRACE_FACILITY                0
#define configUSE_STATS_FORMATTING_FUNCTIONS    0
#define configGENERATE_RUN_TIME_STATS           0
#define configUSE_DAEMON_TASK_STARTUP_HOOK      0

/* Memory Protection - Not available on RISC-V */
#define configENABLE_MPU                        0

/* Interrupt Configuration */
#define configKERNEL_INTERRUPT_PRIORITY         255         // Lowest priority
#define configMAX_SYSCALL_INTERRUPT_PRIORITY    191         // Higher than kernel
#define configMAX_API_CALL_INTERRUPT_PRIORITY   191         // Same as syscall

/* Assert and Error Handling */
#define configASSERT(x)                         if(!(x)) { taskDISABLE_INTERRUPTS(); for(;;); }
#define configUSE_MALLOC_FAILED_HOOK            1           // Enable malloc failed hook
#define configUSE_IDLE_HOOK                     0           // Disable idle hook
#define configUSE_TICK_HOOK                     0           // Disable tick hook
#define configCHECK_FOR_STACK_OVERFLOW          2           // Enable stack overflow check

/* RISC-V Specific Settings */
#define configMTIME                             0xE000BFF8  // RISC-V MTIME register
#define configMTIMECMP                          0xE000C000  // RISC-V MTIMECMP register

/* Optional Functions - Minimal set */
#define INCLUDE_vTaskPrioritySet                0
#define INCLUDE_uxTaskPriorityGet               0
#define INCLUDE_vTaskDelete                     1           // Enable task delete
#define INCLUDE_vTaskSuspend                    1           // Enable task suspend/resume
#define INCLUDE_xResumeFromISR                  0
#define INCLUDE_vTaskDelayUntil                 1           // Enable delay until
#define INCLUDE_vTaskDelay                      1           // Enable task delay
#define INCLUDE_xTaskGetSchedulerState          0
#define INCLUDE_xTaskGetCurrentTaskHandle       1           // Enable get current task
#define INCLUDE_uxTaskGetStackHighWaterMark     0
#define INCLUDE_xTaskGetIdleTaskHandle          0
#define INCLUDE_eTaskGetState                   0
#define INCLUDE_xEventGroupSetBitFromISR        0
#define INCLUDE_xTimerPendFunctionCall          0
#define INCLUDE_xTaskAbortDelay                 0
#define INCLUDE_xTaskGetHandle                  0
#define INCLUDE_xTaskResumeFromISR              0

/* Memory allocation scheme */
#define configSUPPORT_STATIC_ALLOCATION         0           // Dynamic allocation only
#define configSUPPORT_DYNAMIC_ALLOCATION        1           // Enable dynamic allocation

/* Interrupt service routine attribute for RISC-V */
#define portINTERRUPT_ATTRIBUTE                 __attribute__((interrupt("WCH-Interrupt-fast")))

/* Critical section macros for RISC-V */
#define portDISABLE_INTERRUPTS()                __asm volatile("csrc mstatus, 8")
#define portENABLE_INTERRUPTS()                 __asm volatile("csrs mstatus, 8")
#define portENTER_CRITICAL()                    vPortEnterCritical()
#define portEXIT_CRITICAL()                     vPortExitCritical()

/* Yield macro for RISC-V */
#define portYIELD()                             __asm volatile("ecall")

/* Power Management Macros */
#define portSUPPRESS_TICKS_AND_SLEEP(xExpectedIdleTime) vPortSuppressTicksAndSleep(xExpectedIdleTime)

/* Task stack growth direction */
#define portSTACK_GROWTH                        -1          // Stack grows down

/* Byte alignment requirement */
#define portBYTE_ALIGNMENT                      16          // 16-byte alignment for RISC-V

/* Hook function prototypes */
#if (configUSE_MALLOC_FAILED_HOOK == 1)
    extern void vApplicationMallocFailedHook(void);
#endif

#if (configCHECK_FOR_STACK_OVERFLOW > 0)
    extern void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName);
#endif

/* Hardware specific definitions */
#define portINLINE                              __inline

#ifndef portFORCE_INLINE
    #define portFORCE_INLINE                    __forceinline
#endif

/* Memory barrier macros */
#define portMEMORY_BARRIER()                    __asm volatile("fence" ::: "memory")

#endif /* FREERTOS_CONFIG_H */
