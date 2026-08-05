/*
* This source file is part of the EtherCAT Slave Stack Code licensed by Beckhoff Automation GmbH & Co KG, 33415 Verl, Germany.
* The corresponding license agreement applies. This hint shall not be removed.
* https://www.beckhoff.com/media/downloads/slave-stack-code/ethercat_ssc_license.pdf
*/

/**
 * \addtogroup CiA402appl CiA402 Sample Application
 * @{
 */

/**
\file cia402.h
\author EthercatSSC@beckhoff.com
\brief CiA402 specific defines; objects; Axes structure

\version 5.13

<br>Changes to version V5.12:<br>
V5.13 CIA402 1: update names and pdo mapping flags according ETG.6010<br>
<br>Changes to version V5.11:<br>
V5.12 CIA402 1: change define value STATUSWORD_STATE_SWITCHEDONDISABLED<br>
V5.12 CIA402 2: update control word mask for transition 3 (Ready to switch on  to Switched on)<br>
V5.12 CiA402 3: add 16bit padding to process data of csv and csp mode<br>
<br>Changes to version V5.01:<br>
V5.11 CiA402 1: "append padding byte to ""csv/csp"" process data (basic process data has odd word length), add pack directive"<br>
V5.11 COE1: update invalid end entry in the object dictionaries (error with some compilers)<br>
<br>Changes to version - :<br>
V5.01 : Start file change log
 */

/*-----------------------------------------------------------------------------------------
------
------    Includes
------
-----------------------------------------------------------------------------------------*/
#include "objdef.h"

#ifndef _CIA402_H_
#define _CIA402_H_

/*-----------------------------------------------------------------------------------------
------
------    Defines and Types
------
-----------------------------------------------------------------------------------------*/
/*---------------------------------------------
-    ControlWord Commands Mask (IEC61800_184e)
-----------------------------------------------*/
#define CONTROLWORD_COMMAND_SHUTDOWN_MASK                    0x0087 /**< \brief Shutdown command mask*/
#define CONTROLWORD_COMMAND_SWITCHON_MASK                    0x008F /**< \brief Switch on command mask*/
#define CONTROLWORD_COMMAND_SWITCHON_ENABLEOPERATION_MASK    0x008F /**< \brief Switch on & Enable command mask*/
#define CONTROLWORD_COMMAND_DISABLEVOLTAGE_MASK              0x0082 /**< \brief Disable voltage command mask*/
#define CONTROLWORD_COMMAND_QUICKSTOP_MASK                   0x0086 /**< \brief Quickstop command mask*/
#define CONTROLWORD_COMMAND_DISABLEOPERATION_MASK            0x008F /**< \brief Disable operation command mask*/
#define CONTROLWORD_COMMAND_ENABLEOPERATION_MASK             0x008F /**< \brief Enable operation command mask*/
#define CONTROLWORD_COMMAND_FAULTRESET_MASK                  0x0080 /**< \brief Fault reset command mask*/


/*---------------------------------------------
-    ControlWord Commands (IEC61800_184e)
-----------------------------------------------*/
#define CONTROLWORD_COMMAND_SHUTDOWN                         0x0006 /**< \brief Shutdown command*/
#define CONTROLWORD_COMMAND_SWITCHON                         0x0007 /**< \brief Switch on command*/
#define CONTROLWORD_COMMAND_SWITCHON_ENABLEOPERATION         0x000F /**< \brief Switch on & Enable command*/
#define CONTROLWORD_COMMAND_DISABLEVOLTAGE                   0x0000 /**< \brief Disable voltage command*/
#define CONTROLWORD_COMMAND_QUICKSTOP                        0x0002 /**< \brief Quickstop command*/
#define CONTROLWORD_COMMAND_DISABLEOPERATION                 0x0007 /**< \brief Disable operation command*/
#define CONTROLWORD_COMMAND_ENABLEOPERATION                  0x000F /**< \brief Enable operation command*/
#define CONTROLWORD_COMMAND_FAULTRESET                       0x0080 /**< \brief Fault reset command*/


/*---------------------------------------------
-    StatusWord Masks and Flags
-----------------------------------------------*/
#define STATUSWORD_STATE_MASK                                0x006F /**< \brief State mask*/
#define STATUSWORD_VOLTAGE_ENABLED                           0x0010 /**< \brief Indicate high voltage enabled*/
#define STATUSWORD_WARNING                                   0x0080 /**< \brief Warning active*/
#define STATUSWORD_MANUFACTORSPECIFIC                        0x0100 /**< \brief Manufacturer specific*/
#define STATUSWORD_INTERNAL_LIMIT                            0x0800 /**< \brief Internal limit*/
#define STATUSWORD_REMOTE                                    0x0200 /**< \brief Set if the control word is processed*/
#define STATUSWORD_TARGET_REACHED                            0x0400 /**< \brief Target reached*/
#define STATUSWORD_INTERNALLIMITACTIVE                       0x0800 /**< \brief Internal limit active*/
#define STATUSWORD_DRIVE_FOLLOWS_COMMAND                     0x1000 /**< \brief Drive follows command (used in cyclic synchronous modes)*/


/*---------------------------------------------
-    StatusWord
-----------------------------------------------*/
#define STATUSWORD_STATE_NOTREADYTOSWITCHON                  0x0000 /**< \brief Not ready to switch on*/
#define STATUSWORD_STATE_SWITCHEDONDISABLED                  0x0040 /**< \brief Switched on but disabled*/
#define STATUSWORD_STATE_READYTOSWITCHON                     0x0021 /**< \brief Ready to switch on*/
#define STATUSWORD_STATE_SWITCHEDON                          0x0023 /**< \brief Switched on*/
#define STATUSWORD_STATE_OPERATIONENABLED                    0x0027 /**< \brief Operation enabled*/
#define STATUSWORD_STATE_QUICKSTOPACTIVE                     0x0007 /**< \brief Quickstop active*/
#define STATUSWORD_STATE_FAULTREACTIONACTIVE                 0x000F /**< \brief Fault reaction active*/
#define STATUSWORD_STATE_FAULT                               0x0008 /**< \brief Fault state*/


/*---------------------------------------------
-    CiA402 State machine
-----------------------------------------------*/
#define STATE_NOT_READY_TO_SWITCH_ON        0x0001 /**< \brief Not ready to switch on (optional)*/
#define STATE_SWITCH_ON_DISABLED            0x0002 /**< \brief Switch on but disabled (optional)*/
#define STATE_READY_TO_SWITCH_ON            0x0004 /**< \brief Ready to switch on (mandatory)*/
#define STATE_SWITCHED_ON                   0x0008 /**< \brief Switch on (mandatory)*/
#define STATE_OPERATION_ENABLED             0x0010 /**< \brief Operation enabled (mandatory)*/
#define STATE_QUICK_STOP_ACTIVE             0x0020 /**< \brief Quick stop active (optional)*/
#define STATE_FAULT_REACTION_ACTIVE         0x0040 /**< \brief Fault reaction active (mandatory)*/
#define STATE_FAULT                         0x0080 /**< \brief Fault state (mandatory)*/


/*---------------------------------------------
-    CiA402 Modes of Operation (object 0x6060) (IEC61800_184e)
-----------------------------------------------*/
// -128 to -1 Manufacturer-specific operation modes
#define NO_MODE                     0 /**< \brief No mode*/
#define PROFILE_POSITION_MODE       1 /**< \brief Position Profile mode*/
#define VELOCITY_MODE               2 /**< \brief Velocity mode*/
#define PROFILE_VELOCITY_MOCE       3 /**< \brief Velocity Profile mode*/
#define PROFILE_TORQUE_MODE         4 /**< \brief Torque Profile mode*/
//5 reserved                          
#define HOMING_MODE                 6 /**< \brief Homing mode*/
#define INTERPOLATION_POSITION_MODE 7 /**< \brief Interpolation Position mode*/
#define CYCLIC_SYNC_POSITION_MODE   8 /**< \brief Cyclic Synchronous Position mode*/
#define CYCLIC_SYNC_VELOCITY_MODE   9 /**< \brief Cyclic Synchronous Velocity mode*/
#define CYCLIC_SYNC_TORQUE_MODE     10/**< \brief Cyclic Synchronous Torque mode*/
//+11 to +127 reserved


/***************************************
 CiA402 Error Codes (object 0x603F) (IEC61800_184e)
 ***************************************/
#define ERROR_SHORT_CIRCUIT_EARTH_LEAKAGE_INPUT             0x2110 /**< \brief Short circuit/earth leakage (input)*/
#define ERROR_EARTH_LEAKAGE_INPUT                           0x2120 /**< \brief Earth leakage (input)*/
#define ERROR_EARTH_LEAKAGE_PHASE_L1                        0x2121 /**< \brief Earth leakage phase L1*/
#define ERROR_EARTH_LEAKAGE_PHASE_L2                        0x2122 /**< \brief Earth leakage phase L2*/
#define ERROR_EARTH_LEAKAGE_PHASE_L3                        0x2123 /**< \brief Earth leakage phase L3*/
#define ERROR_SHORT_CIRCUIT_INPUT                           0x2130 /**< \brief Short circuit (input)*/
#define ERROR_SHORT_CIRCUIT_PHASES_L1_L2                    0x2131 /**< \brief Short circuit phases L1-L2*/
#define ERROR_SHORT_CIRCUIT_PHASES_L2_L3                    0x2132 /**< \brief Short circuit phases L2-L3*/
#define ERROR_SHORT_CIRCUIT_PHASES_L3_L1                    0x2133 /**< \brief Short circuit phases L3-L1*/
#define ERROR_INTERNAL_CURRENT_NO1                          0x2211 /**< \brief Internal current no 1*/
#define ERROR_INTERNAL_CURRENT_NO2                          0x2212 /**< \brief Internal current no 2*/
#define ERROR_OVER_CURRENT_IN_RAMP_FUNCTION                 0x2213 /**< \brief Over-current in ramp function*/
#define ERROR_OVER_CURRENT_IN_THE_SEQUENCE                  0x2214 /**< \brief Over-current in the sequence*/
#define ERROR_CONTINUOUS_OVER_CURRENT_DEVICE_INTERNAL       0x2220 /**< \brief Continuous over current (device internal)*/
#define ERROR_CONTINUOUS_OVER_CURRENT_DEVICE_INTERNAL_NO1   0x2221 /**< \brief Continuous over current no 1*/
#define ERROR_CONTINUOUS_OVER_CURRENT_DEVICE_INTERNAL_NO2   0x2222 /**< \brief Continuous over current no 2*/
#define ERROR_SHORT_CIRCUIT_EARTH_LEAKAGE_DEVICE_INTERNAL   0x2230 /**< \brief Short circuit/earth leakage (device internal)*/
#define ERROR_EARTH_LEAKAGE_DEVICE_INTERNAL                 0x2240 /**< \brief Earth leakage (device internal)*/
#define ERROR_SHORT_CIRCUIT_DEVICE_INTERNAL                 0x2250 /**< \brief Short circuit (device internal)*/
#define ERROR_CONTINUOUS_OVER_CURRENT                       0x2310 /**< \brief Continuous over current*/
#define ERROR_CONTINUOUS_OVER_CURRENT_NO1                   0x2311 /**< \brief Continuous over current no 1*/
#define ERROR_CONTINUOUS_OVER_CURRENT_NO2                   0x2312 /**< \brief Continuous over current no 2*/
#define ERROR_SHORT_CIRCUIT_EARTH_LEAKAGE_MOTOR_SIDE        0x2320 /**< \brief Short circuit/earth leakage (motor-side)*/
#define ERROR_EARTH_LEAKAGE_MOTOR_SIDE                      0x2330 /**< \brief Earth leakage (motor-side)*/
#define ERROR_EARTH_LEAKAGE_PHASE_U                         0x2331 /**< \brief Earth leakage phase U*/
#define ERROR_EARTH_LEAKAGE_PHASE_V                         0x2332 /**< \brief Earth leakage phase V*/
#define ERROR_EARTH_LEAKAGE_PHASE_W                         0x2333 /**< \brief Earth leakage phase W*/
#define ERROR_SHORT_CIRCUIT_MOTOR_SIDE                      0x2340 /**< \brief Short circuit (motor-side)*/
#define ERROR_SHORT_CIRCUIT_PHASES_U_V                      0x2341 /**< \brief Short circuit phases U-V*/
#define ERROR_EARTH_LEAKAGE_PHASE_V_W                       0x2342 /**< \brief Earth leakage phase V-W*/
#define ERROR_EARTH_LEAKAGE_PHASE_W_U                       0x2343 /**< \brief Earth leakage phase W-U*/
#define ERROR_LOAD_LEVEL_FAULT_I2T_THERMAL_STATE            0x2350 /**< \brief Load level fault (I2t, thermal state)*/
#define ERROR_LOAD_LEVEL_WARNING_I2T_THERMAL_STATE          0x2351 /**< \brief Load level warning (I2t, thermal state)*/
#define ERROR_MAINS_OVER_VOLTAGE                            0x3110 /**< \brief Mains over-voltage*/
#define ERROR_MAINS_OVER_VOLTAGE_PHASE_L1                   0x3111 /**< \brief Mains over-voltage phase L1*/
#define ERROR_MAINS_OVER_VOLTAGE_PHASE_L2                   0x3112 /**< \brief Mains over-voltage phase L2 */
#define ERROR_MAINS_OVER_VOLTAGE_PHASE_L3                   0x3113 /**< \brief Mains over-voltage phase L3*/
#define ERROR_MAINS_UNDER_VOLTAGE                           0x3120 /**< \brief Mains under-voltage*/
#define ERROR_MAINS_UNDER_VOLTAGE_PHASE_L1                  0x3121 /**< \brief Mains under-voltage phase L1*/
#define ERROR_MAINS_UNDER_VOLTAGE_PHASE_L2                  0x3122 /**< \brief Mains under-voltage phase L2*/
#define ERROR_MAINS_UNDER_VOLTAGE_PHASE_L3                  0x3123 /**< \brief Mains under-voltage phase L3*/
#define ERROR_PHASE_FAILURE                                 0x3130 /**< \brief Phase failure*/
#define ERROR_PHASE_FAILURE_L1                              0x3131 /**< \brief Phase failure L1*/
#define ERROR_PHASE_FAILURE_L2                              0x3132 /**< \brief Phase failure L2*/
#define ERROR_PHASE_FAILURE_L3                              0x3133 /**< \brief Phase failure L3*/
#define ERROR_PHASE_SEQUENCE                                0x3134 /**< \brief Phase sequence*/
#define ERROR_MAINS_FREQUENCY                               0x3140 /**< \brief Mains frequency*/
#define ERROR_MAINS_FREQUENCY_TOO_GREAT                     0x3141 /**< \brief Mains frequency too great*/
#define ERROR_MAINS_FREQUENCY_TOO_SMALL                     0x3142 /**< \brief Mains frequency too small*/
#define ERROR_DC_LINK_OVER_VOLTAGE                          0x3210 /**< \brief DC link over-voltage*/
#define ERROR_OVER_VOLTAGE_NO_1                             0x3211 /**< \brief Over-voltage no  1*/
#define ERROR_OVER_VOLTAGE_NO_2                             0x3212 /**< \brief Over voltage no  2 */
#define ERROR_DC_LINK_UNDER_VOLTAGE                         0x3220 /**< \brief DC link under-voltage*/
#define ERROR_UNDER_VOLTAGE_NO_1                            0x3221 /**< \brief Under-voltage no  1*/
#define ERROR_UNDER_VOLTAGE_NO_2                            0x3222 /**< \brief Under-voltage no  2*/
#define ERROR_LOAD_ERROR                                    0x3230 /**< \brief Load error*/
#define ERROR_OUTPUT_OVER_VOLTAGE                           0x3310 /**< \brief Output over-voltage*/
#define ERROR_OUTPUT_OVER_VOLTAGE_PHASE_U                   0x3311 /**< \brief Output over-voltage phase U*/
#define ERROR_OUTPUT_OVER_VOLTAGE_PHASE_V                   0x3312 /**< \brief Output over-voltage phase V*/
#define ERROR_OUTPUT_OVER_VOLTAGE_PHASE_W                   0x3313 /**< \brief Output over-voltage phase W*/
#define ERROR_ARMATURE_CIRCUIT                              0x3320 /**< \brief Armature circuit*/
#define ERROR_ARMATURE_CIRCUIT_INTERRUPTED                  0x3321 /**< \brief Armature circuit interrupted*/
#define ERROR_FIELD_CIRCUIT                                 0x3330 /**< \brief Field circuit error */
#define ERROR_FIELD_CIRCUIT_INTERRUPTED                     0x3331 /**< \brief Field circuit interrupted*/
#define ERROR_EXCESS_AMBIENT_TEMPERATURE                    0x4110 /**< \brief Excess ambient temperature*/
#define ERROR_TOO_LOW_AMBIENT_TEMPERATURE                   0x4120 /**< \brief Too low ambient temperature*/
#define ERROR_TEMPERATURE_SUPPLY_AIR                        0x4130 /**< \brief Temperature supply air*/
#define ERROR_TEMPERATURE_AIR_OUTLET                        0x4140 /**< \brief Temperature air outlet*/
#define ERROR_EXCESS_TEMPERATURE_DEVICE                     0x4210 /**< \brief Excess temperature device*/
#define ERROR_TOO_LOW_TEMPERATURE_DEVICE                    0x4220 /**< \brief Too low temperature device*/
#define ERROR_TEMPERATURE_DRIVE                             0x4300 /**< \brief Temperature drive error*/
#define ERROR_EXCESS_TEMPERATURE_DRIVE                      0x4310 /**< \brief Excess temperature drive error*/
#define ERROR_TOO_LOW_TEMPERATURE_DRIVE                     0x4320 /**< \brief Too low temperature drive error*/
#define ERROR_TEMPERATURE_SUPPLY                            0x4400 /**< \brief Temperature supply error*/
#define ERROR_EXCESS_TEMPERATURE_SUPPLY                     0x4410 /**< \brief Excess temperature supply*/
#define ERROR_TOO_LOW_TEMPERATURE_SUPPLY                    0x4420 /**< \brief Too low temperature supply*/
#define ERROR_SUPPLY_ERROR                                  0x5100 /**< \brief Supply error*/
#define ERROR_SUPPLY_LOW_VOLTAGE                            0x5110 /**< \brief Supply low voltage*/
#define ERROR_U1_SUPPLY_15V                                 0x5111 /**< \brief U1 = supply +15V/-15V*/
#define ERROR_U2_SUPPLY_24_V                                0x5112 /**< \brief U2 = supply +24 V*/
#define ERROR_U3_SUPPLY_5_V                                 0x5113 /**< \brief U3 = supply +5 V*/
#define ERROR_U4_MANUFACTURER_SPECIFIC                      0x5114 /**< \brief U4 = manufacturer-specific error*/
#define ERROR_U5_MANUFACTURER_SPECIFIC                      0x5115 /**< \brief U5 = manufacturer-specific error*/
#define ERROR_U6_MANUFACTURER_SPECIFIC                      0x5116 /**< \brief U6 = manufacturer-specific error*/
#define ERROR_U7_MANUFACTURER_SPECIFIC                      0x5117 /**< \brief U7 = manufacturer-specific error*/
#define ERROR_U8_MANUFACTURER_SPECIFIC                      0x5118 /**< \brief U8 = manufacturer-specific error*/
#define ERROR_U9_MANUFACTURER_SPECIFIC                      0x5119 /**< \brief U9 = manufacturer-specific error*/
#define ERROR_SUPPLY_INTERMEDIATE_CIRCUIT                   0x5120 /**< \brief Supply intermediate circuit*/
//#define ERROR_CONTROL                                     0x5200
#define ERROR_CONTROL_MEASUREMENT_CIRCUIT                   0x5210 /**< \brief Measurement circuit*/
#define ERROR_CONTROL_COMPUTING_CIRCUIT                     0x5220 /**< \brief Computing circuit*/
#define ERROR_OPERATING_UNIT                                0x5300 /**< \brief Operating unit error*/
#define ERROR_POWER_SECTION                                 0x5400 /**< \brief Power section error*/
#define ERROR_OUTPUT_STAGES                                 0x5410 /**< \brief Output stages error*/
#define ERROR_CHOPPER                                       0x5420 /**< \brief Chopper error*/
#define ERROR_INPUT_STAGES                                  0x5430 /**< \brief Input stages error*/
#define ERROR_CONTACTS_ERROR                                0x5440 /**< \brief Contacts error*/
#define ERROR_CONTACT_1_MANUFACTURER_SPECIFIC               0x5441 /**< \brief Contact 1 = manufacturer-specific error*/
#define ERROR_CONTACT_2_MANUFACTURER_SPECIFIC               0x5442 /**< \brief Contact 2 = manufacturer-specific error*/
#define ERROR_CONTACT_3_MANUFACTURER_SPECIFIC               0x5443 /**< \brief Contact 3 = manufacturer-specific error*/
#define ERROR_CONTACT_4_MANUFACTURER_SPECIFIC               0x5444 /**< \brief Contact 4 = manufacturer-specific error*/
#define ERROR_CONTACT_5_MANUFACTURER_SPECIFIC               0x5445 /**< \brief Contact 5 = manufacturer-specific error*/
#define ERROR_FUSES_ERROR                                   0x5450 /**< \brief Fuses error*/
#define ERROR_S1_L1                                         0x5451 /**< \brief S1 = l1 error*/
#define ERROR_S2_L2                                         0x5452 /**< \brief S2 = l2 error*/
#define ERROR_S3_L3                                         0x5453 /**< \brief S3 = l3 error*/
#define ERROR_S4_MANUFACTURER_SPECIFIC                      0x5454 /**< \brief S4 = manufacturer-specific error*/
#define ERROR_S5_MANUFACTURER_SPECIFIC                      0x5455 /**< \brief S5 = manufacturer-specific error*/
#define ERROR_S6_MANUFACTURER_SPECIFIC                      0x5456 /**< \brief S6 = manufacturer-specific error*/
#define ERROR_S7_MANUFACTURER_SPECIFIC                      0x5457 /**< \brief S7 = manufacturer-specific error*/
#define ERROR_S8_MANUFACTURER_SPECIFIC                      0x5458 /**< \brief S8 = manufacturer-specific error*/
#define ERROR_S9_MANUFACTURER_SPECIFIC                      0x5459 /**< \brief S9 = manufacturer-specific error*/
#define ERROR_HARDWARE_MEMORY                               0x5500 /**< \brief Hardware memory error*/
#define ERROR_RAM                                           0x5510 /**< \brief RAM error*/
#define ERROR_ROM_EPROM                                     0x5520 /**< \brief ROM/EPROM error*/
#define ERROR_EEPROM                                        0x5530 /**< \brief EEPROM error*/
#define ERROR_SOFTWARE_RESET_WATCHDOG                       0x6010 /**< \brief Software reset (watchdog)*/
//0x6301_TO_0x630F        ERROR_DATA_RECORD_NO_1_TO_NO_15          
#define ERROR_LOSS_OF_PARAMETERS                            0x6310 /**< \brief Loss of parameters*/
#define ERROR_PARAMETER_ERROR                               0x6320 /**< \brief Parameter error*/
#define ERROR_POWER_ERROR                                   0x7100 /**< \brief Power error*/
#define ERROR_BRAKE_CHOPPER                                 0x7110 /**< \brief Brake chopper*/
#define ERROR_FAILURE_BRAKE_CHOPPER                         0x7111 /**< \brief Failure brake chopper*/
#define ERROR_OVER_CURRENT_BRAKE_CHOPPER                    0x7112 /**< \brief Over current brake chopper*/
#define ERROR_PROTECTIVE_CIRCUIT_BRAKE_CHOPPER              0x7113 /**< \brief Protective circuit brake chopper error*/
#define ERROR_MOTOR_ERROR                                   0x7120 /**< \brief Motor error*/
#define ERROR_MOTOR_BLOCKED                                 0x7121 /**< \brief Motor blocked error*/
#define ERROR_MOTOR_ERROR_OR_COMMUTATION_MALFUNC            0x7122 /**< \brief Motor error or commutation malfunc */
#define ERROR_MOTOR_TILTED                                  0x7123 /**< \brief Motor tilted*/
#define ERROR_MEASUREMENT_CIRCUIT                           0x7200 /**< \brief Measurement circuit*/
#define ERROR_SENSOR_ERROR                                  0x7300 /**< \brief Sensor error*/
#define ERROR_TACHO_FAULT                                   0x7301 /**< \brief Tacho fault*/
#define ERROR_TACHO_WRONG_POLARITY                          0x7302 /**< \brief Tacho wrong polarity*/
#define ERROR_RESOLVER_1_FAULT                              0x7303 /**< \brief Resolver 1 fault*/
#define ERROR_RESOLVER_2_FAULT                              0x7304 /**< \brief Resolver 2 fault*/
#define ERROR_INCREMENTAL_SENSOR_1_FAULT                    0x7305 /**< \brief Incremental sensor 1 fault*/
#define ERROR_INCREMENTAL_SENSOR_2_FAULT                    0x7306 /**< \brief Incremental sensor 2 fault*/
#define ERROR_INCREMENTAL_SENSOR_3_FAULT                    0x7307 /**< \brief Incremental sensor 3 fault*/
#define ERROR_SPEED                                         0x7310 /**< \brief Speed error*/
#define ERROR_POSITION                                      0x7320 /**< \brief Position error*/
#define ERROR_COMPUTATION_CIRCUIT                           0x7400 /**< \brief Computation circuit*/
#define ERROR_COMMUNICATION                                 0x7500 /**< \brief Communication error*/
#define ERROR_SERIAL_INTERFACE_NO_1                         0x7510 /**< \brief Serial interface no  1 error*/
#define ERROR_SERIAL_INTERFACE_NO_2                         0x7520 /**< \brief Serial interface no  2 error*/
#define ERROR_DATA_STORAGE_EXTERNAL                         0x7600 /**< \brief Data storage (external) error*/
#define ERROR_TORQUE_CONTROL                                0x8300 /**< \brief Torque control error*/
#define ERROR_EXCESS_TORQUE                                 0x8311 /**< \brief Excess torque error*/
#define ERROR_DIFFICULT_START_UP                            0x8312 /**< \brief Difficult start up error*/
#define ERROR_STANDSTILL_TORQUE                             0x8313 /**< \brief Standstill torque error*/
#define ERROR_INSUFFICIENT_TORQUE                           0x8321 /**< \brief Insufficient torque error*/
#define ERROR_TORQUE_FAULT                                  0x8331 /**< \brief Torque fault*/
#define ERROR_VELOCITY_SPEED_CONTROLLER                     0x8400 /**< \brief Velocity speed controller*/
#define ERROR_POSITION_CONTROLLER                           0x8500 /**< \brief Position controller*/
#define ERROR_POSITIONING_CONTROLLER                        0x8600 /**< \brief Positioning controller*/
#define ERROR_FOLLOWING_ERROR                               0x8611 /**< \brief Following error*/
#define ERROR_REFERENCE_LIMIT                               0x8612 /**< \brief Reference limit*/
#define ERROR_SYNC_CONTROLLER                               0x8700 /**< \brief Sync controller*/
#define ERROR_WINDING_CONTROLLER                            0x8800 /**< \brief Winding controller*/
#define ERROR_PROCESS_DATA_MONITORING                       0x8900 /**< \brief Process data monitoring*/
//#define ERROR_CONTROL                                     0x8A00
#define ERROR_DECELERATION                                  0xF001 /**< \brief Deceleration error*/
#define ERROR_SUB_SYNCHRONOUS_RUN                           0xF002 /**< \brief Sub-synchronous run error*/
#define ERROR_STROKE_OPERATION                              0xF003 /**< \brief Stroke operation error*/
//#define ERROR_CONTROL                                     0xF004
//0xFF00_TO_0xFFFF        MANUFACTURER_SPECIFIC                   


/*---------------------------------------------
-    CiA402 generic error option code values
        Note: Not all values are valid for each error option code.
        A detailed description of the option code values are listed in the specification IEC 61800-7-200
        0x605B    : action in state transition 8
        0x605C    : action in state transition 5
-----------------------------------------------*/
#define DISABLE_DRIVE                    0 /**< \brief Disable drive (options: 0x605B; 0x605C; 0x605E)*/
#define SLOW_DOWN_RAMP                   1 /**< \brief Slow down ramp (options: 0x605B; 0x605C; 0x605E)*/
#define QUICKSTOP_RAMP                   2 /**< \brief Quick stop ramp (options: 0x605E)*/
#define STOP_ON_CURRENT_LIMIT            3 /**< \brief Stop on current limit (options: 0x605E)*/
#define STOP_ON_VOLTAGE_LIMIT            4 /**< \brief Stop on voltage limit (options: 0x605E)*/


/*---------------------------------------------
-    Specific values for Quick stop option code (object 0x605A) (IEC61800_184e)
        indicated the quick stop function
-----------------------------------------------*/
//-32768 to -1        MANUFACTURER_SPECIFIC
#define SLOWDOWN_RAMP_NO_TRANSIT                5 /**< \brief Slow down on slow down ramp and stay in Quick Stop Active*/
#define QUICKSTOP_RAMP_NO_TRANSIT               6 /**< \brief Slow down on quick stop ramp and stay in Quick Stop Active*/
#define CURRENT_LIMIT_NO_TRANSIT                7 /**< \brief Slow down on current limit and stay in Quick Stop Active*/
#define VOLTAGE_LIMIT_NO_TRANSIT                8 /**< \brief Slow down on voltage limit and stay in Quick Stop Active*/
//9 to 32767        RESERVED


#define MAX_AXES    1 /**< \brief Number of supported axes*/



/*---------------------------------------------
-    Module Identifications (each supported operation mode has a module)
-----------------------------------------------*/
#define CSV_CSP_MODULE_ID       0x00119800 /**< \brief Module Id for cyclic synchronous position/velocity mode (dynamic switching supported)*/
#define CSP_MODULE_ID           0x00219800 /**< \brief Module Id for cyclic synchronous position mode*/
#define CSV_MODULE_ID           0x00319800 /**< \brief Module Id for cyclic synchronous velocity mode*/


/**
 * \addtogroup PdoMappingObjects PDO Mapping Objects
 * csp/csv mode RxPDO mapping : 0x1600<br>
 * csp     mode RxPDO mapping : 0x1601<br>
 * csv     mode RxPDO mapping : 0x1602<br>
 * csp/csv mode TxPDO mapping : 0x1A00<br>
 * csp     mode TxPDO mapping : 0x1A01<br>
 * csv     mode TxPDO mapping : 0x1A02
 * @{
 */
/** \brief 0x1600 (csp/csv RxPDO) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   UINT32   aEntries[8]; /**< \brief Entry buffer*/
} OBJ_STRUCT_PACKED_END
TOBJ1600;


/** \brief 0x1601 (csp RxPDO) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   UINT32   aEntries[8]; /**< \brief Entry buffer*/
} OBJ_STRUCT_PACKED_END
TOBJ1601;


/** \brief 0x1602 (csv RxPDO) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   UINT32   aEntries[8]; /**< \brief Entry buffer*/
} OBJ_STRUCT_PACKED_END
TOBJ1602;


/** \brief 0x1A00 (csp/csv TxPDO) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   UINT32   aEntries[8]; /**< \brief Entry buffer*/
} OBJ_STRUCT_PACKED_END
TOBJ1A00;


/** \brief 0x1A01 (csp TxPDO) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   UINT32   aEntries[8]; /**< \brief Entry buffer*/
} OBJ_STRUCT_PACKED_END
TOBJ1A01;


/** \brief 0x1A02 (csv TxPDO) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   UINT32   aEntries[8]; /**< \brief Entry buffer*/
} OBJ_STRUCT_PACKED_END
TOBJ1A02;
/** @}*/


/**
 * \addtogroup SmAssignObjects SyncManager Assignment Objects
 * SyncManager 2 : 0x1C12<br>
 * SyncManager 3 : 0x1C13
 * @{
 */
/** \brief 0x1C12 (SyncManager 2 assignment) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   UINT16   aEntries[MAX_AXES]; /**< \brief Entry buffer (number of entries depends on the supported axis, each axis requires one entry)*/
} OBJ_STRUCT_PACKED_END
TOBJ1C12;


/** \brief 0x1C13 (SyncManager 3 assignment) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   UINT16   aEntries[MAX_AXES]; /**< \brief Entry buffer (number of entries depends on the supported axis, each axis requires one entry)*/
} OBJ_STRUCT_PACKED_END
TOBJ1C13;
/** @}*/


/**
 * \addtogroup CiA402Objects CiA402 Axis Objects
 * @{
 */
/** \brief 0x607D (Software Position Limit) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   INT32    i32MinLimit; /**< \brief Minimum limit*/
   INT32    i32MaxLimit; /**< \brief Maximum limit*/
} OBJ_STRUCT_PACKED_END
TOBJ607D;


/** \brief Object 0x60C2 (Interpolation Time Period) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex 0*/
   UINT8    u8InterpolationPeriod; /**< \brief Interpolation period*/
   INT8     i8InterpolationIndex; /**< \brief Interpolation index*/
} OBJ_STRUCT_PACKED_END
TOBJ60C2;
/** @}*/


/**
 * \addtogroup DeviceParaObjects Device Parameter Objects
 * Modular Device Profile : 0xF000<br>
 * Module Profile List : 0xF010<br>
 * Configured Modules Ident List : 0xF030<br>
 * Detected Modules Ident List : 0xF050<br>
 * @{
 */
/** \brief 0xF000 (Modular Device Profile) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex0*/
   UINT16   u16Moduleindexdistance; /**< \brief Module Index distance
                                     * 
                                     * Index distance between two modules.<br>
                                     * According to ETG.6010 the object index distance is 0x800*/
   UINT16   u16Maximumnumberofmodules; /**< \brief Maximum number of modules*/
} OBJ_STRUCT_PACKED_END
TOBJF000;


/** \brief 0xF010 (Module Profile List) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex0*/
   UINT32   aEntries[MAX_AXES];/**< \brief Module profile information buffer
                                  * 
                                  * Bit 00..15: Profile number of the module on position 1<br>
                                  * Bit 16..31: Profile specific<br>
                                  * The number of entries depends on the number of supported axes.
                                  */
} OBJ_STRUCT_PACKED_END
TOBJF010;


/** \brief 0xF030 (Configured Modules Ident List) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex0*/
   UINT32   aEntries[MAX_AXES];/**< \brief Module Ident List buffer
                                  * The number of entries depends on the number of supported axes.
                                  */
} OBJ_STRUCT_PACKED_END
TOBJF030;


/** \brief 0xF050 (Detected Modules Ident List) data structure*/
typedef struct OBJ_STRUCT_PACKED_START {
   UINT16   u16SubIndex0; /**< \brief SubIndex0*/
   UINT32   aEntries[MAX_AXES];/**< \brief Module Ident List buffer
                                  * The number of entries depends on the number of supported axes.
                                  */
} OBJ_STRUCT_PACKED_END
TOBJF050;
/** @}*/


/*---------------------------------------------
-    Generic Axis structure
-----------------------------------------------*/
/**
 * \addtogroup PDO Process Data Objects
 * @{
 */
/** \brief Data structure to handle the process data transmitted via 0x1A00 (csp/csv TxPDO)*/
typedef struct STRUCT_PACKED_START
{
    UINT16 ObjStatusWord; /**< \brief Status word (0x6041)*/
    INT16 ObjModesOfOperationDisplay; /**< \brief Current mode of operation (0x6061)*/
    INT32 ObjVelocityActualValue; /**< \brief Actual velocity (0x606C)*/
    INT32 ObjPositionActualValue; /**< \brief Actual position (0x6064)*/
}STRUCT_PACKED_END
TCiA402PDO1A00;


/** \brief Data structure to handle the process data transmitted via 0x1A01 (csp TxPDO)*/
typedef struct STRUCT_PACKED_START
{
    UINT16 ObjStatusWord; /**< \brief Status word (0x6041)*/
    INT16 ObjModesOfOperationDisplay; /**< \brief Current mode of operation (0x6061)*/
    INT32 ObjVelocityActualValue; /**< \brief Actual velocity (0x606C)*/
    INT32 ObjPositionActualValue; /**< \brief Actual position (0x6064)*/
}STRUCT_PACKED_END
TCiA402PDO1A01;


/** \brief Data structure to handle the process data transmitted via 0x1A02 (csv TxPDO)*/
typedef struct STRUCT_PACKED_START
{
    UINT16 ObjStatusWord; /**< \brief Status word (0x6041)*/
    INT32 ObjPositionActualValue; /**< \brief Actual position (0x6064)*/
    UINT16 Padding16Bit; /**< \brief 16bit padding*/
}STRUCT_PACKED_END
TCiA402PDO1A02;


/** \brief Data structure to handle the process data transmitted via 0x1600 (csp/csv RxPDO)*/
typedef struct STRUCT_PACKED_START
{
    UINT16 ObjControlWord; /**< \brief Control word (0x6040)*/
    INT32 ObjTargetPosition; /**< \brief Target position (0x607A)*/
    INT32 ObjTargetVelocity; /**< \brief Target velocity (0x60FF)*/
    INT16 ObjModesOfOperation; /**< \brief Mode of operation (0x6060)*/
}STRUCT_PACKED_END
TCiA402PDO1600;


/** \brief Data structure to handle the process data transmitted via 0x1601 (csp RxPDO)*/
typedef struct STRUCT_PACKED_START
{
    UINT16 ObjControlWord; /**< \brief Control word (0x6040)*/
    INT16  ObjModesOfOperation; /**< \brief Mode of operation (0x6060)*/
    INT32  ObjTargetVelocity; /**< \brief Target velocity (0x60FF)*/
    INT32  ObjTargetPosition; /**< \brief Target position (0x607A)*/
}STRUCT_PACKED_END
TCiA402PDO1601;


/** \brief Data structure to handle the process data transmitted via 0x1602 (csv RxPDO)*/
typedef struct STRUCT_PACKED_START
{
    UINT16 ObjControlWord; /**< \brief Control word (0x6040)*/
    INT32 ObjTargetVelocity; /**< \brief Target velocity (0x60FF)*/
    UINT16 Padding16Bit; /**< \brief 16bit padding*/
}STRUCT_PACKED_END
TCiA402PDO1602;
/** @}*/



/**
 * \addtogroup CiA402Objects CiA402 Axis Objects
 * @{
 */
/* BEGIN GENERATED EDS OBJECT TYPES */
/* Generated by generate_cia402.py. Do not edit this block manually. */
/** \brief Object 0x1603 (Receive PDO 4 Mapping) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT32 aEntries[8]; /**< \brief SubIndex 1..8. */
} OBJ_STRUCT_PACKED_END
TOBJ1603;

/** \brief Object 0x1A03 (Transmit PDO 4 Mapping) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT32 aEntries[8]; /**< \brief SubIndex 1..8. */
} OBJ_STRUCT_PACKED_END
TOBJ1A03;

/** \brief Object 0x200A (NFC memory manage) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT32 globalErrors; /**< \brief 0x200A:01 Global errors. */
    UINT32 password; /**< \brief 0x200A:02 Password. */
    UINT32 commands; /**< \brief 0x200A:03 Commands. */
    UINT32 commandReadSingleObject; /**< \brief 0x200A:04 Command read single object. */
    UINT32 valueReadSingleObject; /**< \brief 0x200A:05 Value read single object. */
    UINT32 commandWriteSingleObject; /**< \brief 0x200A:06 Command write single object. */
    UINT32 valueWriteSingleObject; /**< \brief 0x200A:07 Value write single object. */
    UINT32 errorsStatesCanopenCommands; /**< \brief 0x200A:08 Errors states canopen commands. */
    UINT16 memorySize; /**< \brief 0x200A:09 Memory size. */
    UINT16 errorsHistorySize; /**< \brief 0x200A:0A Errors history size. */
    UINT32 statusRegister; /**< \brief 0x200A:0B Status register. */
} OBJ_STRUCT_PACKED_END
TOBJ200A;

/** \brief Object 0x200B (Input output configuration) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT8 aEntries[10]; /**< \brief SubIndex 1..10. */
} OBJ_STRUCT_PACKED_END
TOBJ200B;

/** \brief Object 0x200C (Motor constants) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    REAL32 aEntries[3]; /**< \brief SubIndex 1..3. */
} OBJ_STRUCT_PACKED_END
TOBJ200C;

/** \brief Object 0x2015 (I2t) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT16 thresholdCurrent; /**< \brief 0x2015:01 Threshold current. */
    UINT16 thresholdTime; /**< \brief 0x2015:02 Threshold time. */
    UINT32 faultValue; /**< \brief 0x2015:03 Fault value. */
    UINT32 currentValue; /**< \brief 0x2015:04 Current value. */
} OBJ_STRUCT_PACKED_END
TOBJ2015;

/** \brief Object 0x2027 (Commands) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    BOOL aEntries[3]; /**< \brief SubIndex 1..3. */
} OBJ_STRUCT_PACKED_END
TOBJ2027;

/** \brief Object 0x2028 (Error field time) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT32 aEntries[100]; /**< \brief SubIndex 1..100. */
} OBJ_STRUCT_PACKED_END
TOBJ2028;

/** \brief Object 0x202B (VDC Power Limits) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT16 aEntries[4]; /**< \brief SubIndex 1..4. */
} OBJ_STRUCT_PACKED_END
TOBJ202B;

/** \brief Object 0x202D (Manufacturer 17) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT32 aEntries[8]; /**< \brief SubIndex 1..8. */
} OBJ_STRUCT_PACKED_END
TOBJ202D;

/** \brief Object 0x6091 (Gear ratio) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT32 aEntries[2]; /**< \brief SubIndex 1..2. */
} OBJ_STRUCT_PACKED_END
TOBJ6091;

/** \brief Object 0x6092 (Feed constant) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT32 aEntries[2]; /**< \brief SubIndex 1..2. */
} OBJ_STRUCT_PACKED_END
TOBJ6092;

/** \brief Object 0x6099 (Homing speeds) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT32 aEntries[2]; /**< \brief SubIndex 1..2. */
} OBJ_STRUCT_PACKED_END
TOBJ6099;

/** \brief Object 0x60C1 (Interpolation data record) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    INT32 aEntries[50]; /**< \brief SubIndex 1..50. */
} OBJ_STRUCT_PACKED_END
TOBJ60C1;

/** \brief Object 0x60C4 (Interpolation data configuration) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    UINT32 maximumBufferSize; /**< \brief 0x60C4:01 Maximum buffer size. */
    UINT32 actualBufferSize; /**< \brief 0x60C4:02 Actual buffer size. */
    BOOL bufferOrganisation; /**< \brief 0x60C4:03 Buffer organisation. */
    UINT16 bufferPosition; /**< \brief 0x60C4:04 Buffer position. */
    UINT8 sizeOfDataRecord; /**< \brief 0x60C4:05 Size of data record. */
    BOOL bufferClear; /**< \brief 0x60C4:06 Buffer clear. */
} OBJ_STRUCT_PACKED_END
TOBJ60C4;

/** \brief Object 0x60F6 (Current control parameter set) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    REAL32 aEntries[2]; /**< \brief SubIndex 1..2. */
} OBJ_STRUCT_PACKED_END
TOBJ60F6;

/** \brief Object 0x60F9 (Velocity control parameter set) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    REAL32 aEntries[2]; /**< \brief SubIndex 1..2. */
} OBJ_STRUCT_PACKED_END
TOBJ60F9;

/** \brief Object 0x60FB (Position control parameter set) data structure. */
typedef struct OBJ_STRUCT_PACKED_START
{
    UINT16 u16SubIndex0; /**< \brief SubIndex 0, stored as UINT16 by SSC. */
    REAL32 aEntries[6]; /**< \brief SubIndex 1..6. */
} OBJ_STRUCT_PACKED_END
TOBJ60FB;
/* END GENERATED EDS OBJECT TYPES */

/** \brief Data structure containing all selected EDS axis/manufacturer objects. */
typedef struct OBJ_STRUCT_PACKED_START
{
    TOBJ1600 sRxPDOMap0; /**< \brief 0x1600 Receive PDO 1 Mapping. */
    TOBJ1601 sRxPDOMap1; /**< \brief 0x1601 Receive PDO 2 Mapping. */
    TOBJ1602 sRxPDOMap2; /**< \brief 0x1602 Receive PDO 3 Mapping. */
    TOBJ1603 sRxPDOMap3; /**< \brief 0x1603 Receive PDO 4 Mapping. */
    TOBJ1A00 sTxPDOMap0; /**< \brief 0x1A00 Transmit PDO 1 Mapping. */
    TOBJ1A01 sTxPDOMap1; /**< \brief 0x1A01 Transmit PDO 2 Mapping. */
    TOBJ1A02 sTxPDOMap2; /**< \brief 0x1A02 Transmit PDO 3 Mapping. */
    TOBJ1A03 sTxPDOMap3; /**< \brief 0x1A03 Transmit PDO 4 Mapping. */
    UINT16 objRiddenAngle; /**< \brief 0x2000 Ridden angle. */
    UINT32 objEnableFunctionality; /**< \brief 0x2001 Enable functionality. */
    UINT32 objEncoderOutPulsePerTurn; /**< \brief 0x2002 Encoder out pulse per turn. */
    REAL32 objN12VVoltage; /**< \brief 0x2003 12V voltage. */
    REAL32 objN4VVoltage; /**< \brief 0x2004 4V voltage. */
    REAL32 objN3V3Voltage; /**< \brief 0x2005 3V3 voltage. */
    UINT32 objHomingCurrentSaturation; /**< \brief 0x2006 Homing current saturation. */
    UINT32 objHomingTorqueSaturation; /**< \brief 0x2007 Homing torque saturation. */
    UINT32 objHomingSaturationTime; /**< \brief 0x2008 Homing saturation time. */
    REAL32 objAngleOffset; /**< \brief 0x2009 Angle offset. */
    TOBJ200A objNFCMemoryManage; /**< \brief 0x200A NFC memory manage. */
    TOBJ200B objInputOutputConfiguration; /**< \brief 0x200B Input output configuration. */
    TOBJ200C objMotorConstants; /**< \brief 0x200C Motor constants. */
    REAL32 objN24VVoltage; /**< \brief 0x200D 24V voltage. */
    REAL32 objN24VVoltageError; /**< \brief 0x200E 24V voltage error. */
    REAL32 objTemperatureUC; /**< \brief 0x200F Temperature uC. */
    REAL32 objIuOffset; /**< \brief 0x2010 Iu offset. */
    REAL32 objIvOffset; /**< \brief 0x2011 Iv offset. */
    REAL32 objIwOffset; /**< \brief 0x2012 Iw offset. */
    UINT32 objCommunicationErrorIndex; /**< \brief 0x2013 Communication error index. */
    UINT32 objWarningRegister; /**< \brief 0x2014 Warning register. */
    TOBJ2015 objI2t; /**< \brief 0x2015 I2t. */
    UINT16 objInOutMonitor; /**< \brief 0x2016 In out monitor. */
    UINT32 objManufacturer01; /**< \brief 0x2017 Manufacturer 01. */
    UINT32 objManufacturer02; /**< \brief 0x2018 Manufacturer 02. */
    UINT32 objManufacturer03; /**< \brief 0x2019 Manufacturer 03. */
    UINT32 objManufacturer04; /**< \brief 0x201A Manufacturer 04. */
    INT32 objManufacturer05; /**< \brief 0x201B Manufacturer 05. */
    INT32 objManufacturer06; /**< \brief 0x201C Manufacturer 06. */
    INT32 objManufacturer07; /**< \brief 0x201D Manufacturer 07. */
    INT32 objManufacturer08; /**< \brief 0x201E Manufacturer 08. */
    REAL32 objManufacturer09; /**< \brief 0x201F Manufacturer 09. */
    REAL32 objManufacturer10; /**< \brief 0x2020 Manufacturer 10. */
    REAL32 objManufacturer11; /**< \brief 0x2021 Manufacturer 11. */
    REAL32 objManufacturer12; /**< \brief 0x2022 Manufacturer 12. */
    UINT32 objManufacturer13; /**< \brief 0x2023 Manufacturer 13. */
    UINT32 objManufacturer14; /**< \brief 0x2024 Manufacturer 14. */
    UINT32 objManufacturer15; /**< \brief 0x2025 Manufacturer 15. */
    UINT32 objManufacturer16; /**< \brief 0x2026 Manufacturer 16. */
    TOBJ2027 objCommands; /**< \brief 0x2027 Commands. */
    TOBJ2028 objErrorFieldTime; /**< \brief 0x2028 Error field time. */
    UINT32 objCurrentTime; /**< \brief 0x2029 Current time. */
    INT32 objSensorToReferenceDistance; /**< \brief 0x202A Sensor to reference distance. */
    TOBJ202B objVDCPowerLimits; /**< \brief 0x202B VDC Power Limits. */
    TOBJ202D objManufacturer17; /**< \brief 0x202D Manufacturer 17. */
    UINT16 objErrorCode; /**< \brief 0x603F Error code. */
    UINT16 objControlWord; /**< \brief 0x6040 Controlword. */
    UINT16 objStatusWord; /**< \brief 0x6041 Statusword. */
    INT16 objQuickStopOptionCode; /**< \brief 0x605A Quick stop option code. */
    INT16 objShutdownOptionCode; /**< \brief 0x605B Shutdown option code. */
    INT16 objDisableOperationOptionCode; /**< \brief 0x605C Disable Operation Option Code. */
    INT16 objHaltOptionCode; /**< \brief 0x605D Halt option code. */
    INT16 objFaultReactionCode; /**< \brief 0x605E Fault reaction option code. */
    INT8 objModesOfOperation; /**< \brief 0x6060 Modes of operation. */
    INT8 objModesOfOperationDisplay; /**< \brief 0x6061 Modes of operation display. */
    INT32 objPositionDemandValue; /**< \brief 0x6062 Position demand value. */
    INT32 objPositionActualInternalValue; /**< \brief 0x6063 Position actual internal value. */
    INT32 objPositionActualValue; /**< \brief 0x6064 Position actual value. */
    UINT32 objFollowingErrorWindow; /**< \brief 0x6065 Following error window. */
    UINT16 objFollowingErrorTimeOut; /**< \brief 0x6066 Following error time out. */
    UINT32 objPositionWindow; /**< \brief 0x6067 Position window. */
    UINT16 objPositionWindowTime; /**< \brief 0x6068 Position window time. */
    INT32 objVelocityDemandValue; /**< \brief 0x606B Velocity demand value. */
    INT32 objVelocityActualValue; /**< \brief 0x606C Velocity actual value. */
    UINT16 objVelocityWindow; /**< \brief 0x606D Velocity window. */
    UINT16 objVelocityWindowTime; /**< \brief 0x606E Velocity window time. */
    UINT16 objVelocityThreshold; /**< \brief 0x606F Velocity threshold. */
    UINT16 objVelocityThresholdTime; /**< \brief 0x6070 Velocity threshold time. */
    INT16 objTargetTorque; /**< \brief 0x6071 Target torque. */
    UINT16 objMaxTorque; /**< \brief 0x6072 Max torque. */
    UINT16 objMaxCurrent; /**< \brief 0x6073 Max current. */
    INT16 objTorqueDemand; /**< \brief 0x6074 Torque demand. */
    UINT32 objMotorRatedCurrent; /**< \brief 0x6075 Motor rated current. */
    UINT32 objMotorRatedTorque; /**< \brief 0x6076 Motor rated torque. */
    INT16 objTorqueActualValue; /**< \brief 0x6077 Torque actual value. */
    INT16 objCurrentActualValue; /**< \brief 0x6078 Current actual value. */
    UINT32 objDCLinkCircuitVoltage; /**< \brief 0x6079 DC link circuit voltage. */
    INT32 objTargetPosition; /**< \brief 0x607A Target position. */
    INT32 objHomeOffset; /**< \brief 0x607C Home offset. */
    TOBJ607D objSoftwarePositionLimit; /**< \brief 0x607D Software position limit. */
    UINT8 objPolarity; /**< \brief 0x607E Polarity. */
    UINT32 objMaximalProfileVelocity; /**< \brief 0x607F Maximal profile velocity. */
    UINT32 objMaxMotorSpeed; /**< \brief 0x6080 Max motor speed. */
    UINT32 objProfileVelocity; /**< \brief 0x6081 Profile velocity. */
    UINT32 objProfileAcceleration; /**< \brief 0x6083 Profile acceleration. */
    UINT32 objProfileDeceleration; /**< \brief 0x6084 Profile deceleration. */
    UINT32 objQuickStopDeclaration; /**< \brief 0x6085 Quick stop deceleration. */
    INT16 objMotionProfileType; /**< \brief 0x6086 Motion profile type. */
    UINT32 objTorqueSlope; /**< \brief 0x6087 Torque slope. */
    TOBJ6091 objGearRatio; /**< \brief 0x6091 Gear ratio. */
    TOBJ6092 objFeedConstant; /**< \brief 0x6092 Feed constant. */
    INT8 objHomingMethod; /**< \brief 0x6098 Homing method. */
    TOBJ6099 objHomingSpeeds; /**< \brief 0x6099 Homing speeds. */
    UINT32 objHomingAcceleration; /**< \brief 0x609A Homing acceleration. */
    INT16 objInterpolationSubModeSelect; /**< \brief 0x60C0 Interpolation sub mode select. */
    TOBJ60C1 objInterpolationDataRecord; /**< \brief 0x60C1 Interpolation data record. */
    TOBJ60C2 objInterpolationTimePeriod; /**< \brief 0x60C2 Interpolation time period. */
    TOBJ60C4 objInterpolationDataConfiguration; /**< \brief 0x60C4 Interpolation data configuration. */
    UINT32 objMaxAcceleration; /**< \brief 0x60C5 Max acceleration. */
    UINT32 objMaxDeceleration; /**< \brief 0x60C6 Max deceleration. */
    TOBJ60F6 objCurrentControlParameterSet; /**< \brief 0x60F6 Current control parameter set. */
    TOBJ60F9 objVelocityControlParameterSet; /**< \brief 0x60F9 Velocity control parameter set. */
    TOBJ60FB objPositionControlParameterSet; /**< \brief 0x60FB Position control parameter set. */
    INT32 objTargetVelocity; /**< \brief 0x60FF Target velocity. */
    UINT16 objMotorType; /**< \brief 0x6402 Motor type. */
    UINT32 objSupportedDriveModes; /**< \brief 0x6502 Supported drive modes. */
} OBJ_STRUCT_PACKED_END
CiA402Objects;



#define CIA402_OBJECTS_SIZE     SIZEOF(CiA402Objects) /**< \brief Size of CiA402 object structure*/


/** \brief Data structure to handle an Cia402 axis*/
typedef struct
{
    BOOL        bAxisIsActive; /**< \brief Indicates if active is active*/
    BOOL        bBrakeApplied; /**< \brief Motor break is applied*/
    BOOL        bLowLevelPowerApplied; /**< \brief Low Level Power applied*/
    BOOL        bHighLevelPowerApplied; /**< \brief High Level Power applied*/
    BOOL        bAxisFunctionEnabled; /**< \brief Axis functions enabled*/
    BOOL        bConfigurationAllowed; /**< \brief Configuration allowed*/

    UINT16      i16State; /**< \brief Axis state*/
    UINT16      u16PendingOptionCode; /**< \brief Pending operation code*/
    double      fCurPosition; /**< \brief Current position within control loop*/
    UINT32      u32CycleTime; /**< \brief Motion controller cycletime in us*/


    CiA402Objects        Objects; /**< \brief CiA402 Axis object variable*/
    TOBJECT OBJMEM        * ObjDic; /**< \brief Pointer to Axis specific object dictionary*/
}
TCiA402Axis, *pTCiA402Axis;
/** @}*/

#endif //_CIA402_H_

#ifdef _CiA402_
    #define PROTO
#else
    #define PROTO extern
#endif


/*---------------------------------------------
-    Entry Descriptions and object names
-----------------------------------------------*/
#ifdef _CiA402_
/**
 * \addtogroup SmAssignObjects SyncManager Assignment Objects
 * @{
 */

/**
 * \brief Entry descriptions of SyncManager assign objects
 *
 * SubIndex0<br>
 * SubIndex1 (for all other entries the same description will be used (because the object code is ARRAY))
 */
OBJCONST TSDOINFOENTRYDESC    OBJMEM asPDOAssignEntryDesc[] = {
   {DEFTYPE_UNSIGNED8,  0x08, (ACCESS_READ|ACCESS_WRITE_PREOP)},
   {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READ|ACCESS_WRITE_PREOP)}};

   
/**
 * \brief Object 0x1C12 (Sync Manager 2 assign) object and entry names
 *
 * In this example no specific entry name is defined ("SubIndex xxx" is used)
 */   
OBJCONST UCHAR OBJMEM aName0x1C12[] = "RxPDO assign";

/**
 * \brief Object 0x1C13 (Sync Manager 3 assign) object and entry names
 *
 * In this example no specific entry name is defined ("SubIndex xxx" is used)
 */
OBJCONST UCHAR OBJMEM aName0x1C13[] = "TxPDO assign";
/** @}*/


/**
 * \addtogroup PdoMappingObjects PDO Mapping Objects
 * @{
 */
/* BEGIN GENERATED EDS PDO DESCRIPTORS */
/* Generated by generate_cia402.py. Do not edit this block manually. */

/** \brief Object 0x1600 (Receive PDO 1 Mapping) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x1600[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x08 */
};
OBJCONST UCHAR OBJMEM aName0x1600[] = "Receive PDO 1 Mapping\000PDO 1 Mapping for an application object 1\000PDO 1 Mapping for an application object 2\000PDO 1 Mapping for an application object 3\000PDO 1 Mapping for an application object 4\000PDO 1 Mapping for an application object 5\000PDO 1 Mapping for an application object 6\000PDO 1 Mapping for an application object 7\000PDO 1 Mapping for an application object 8\000\377";

/** \brief Object 0x1601 (Receive PDO 2 Mapping) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x1601[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x08 */
};
OBJCONST UCHAR OBJMEM aName0x1601[] = "Receive PDO 2 Mapping\000PDO 2 Mapping for an application object 1\000PDO 2 Mapping for an application object 2\000PDO 2 Mapping for an application object 3\000PDO 2 Mapping for an application object 4\000PDO 2 Mapping for an application object 5\000PDO 2 Mapping for an application object 6\000PDO 2 Mapping for an application object 7\000PDO 2 Mapping for an application object 8\000\377";

/** \brief Object 0x1602 (Receive PDO 3 Mapping) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x1602[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x08 */
};
OBJCONST UCHAR OBJMEM aName0x1602[] = "Receive PDO 3 Mapping\000PDO 3 Mapping for an application object 1\000PDO 3 Mapping for an application object 2\000PDO 3 Mapping for an application object 3\000PDO 3 Mapping for an application object 4\000PDO 3 Mapping for an application object 5\000PDO 3 Mapping for an application object 6\000PDO 3 Mapping for an application object 7\000PDO 3 Mapping for an application object 8\000\377";

/** \brief Object 0x1603 (Receive PDO 4 Mapping) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x1603[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x08 */
};
OBJCONST UCHAR OBJMEM aName0x1603[] = "Receive PDO 4 Mapping\000PDO 4 Mapping for an application object 1\000PDO 4 Mapping for an application object 2\000PDO 4 Mapping for an application object 3\000PDO 4 Mapping for an application object 4\000PDO 4 Mapping for an application object 5\000PDO 4 Mapping for an application object 6\000PDO 4 Mapping for an application object 7\000PDO 4 Mapping for an application object 8\000\377";

/** \brief Object 0x1A00 (Transmit PDO 1 Mapping) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x1A00[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x08 */
};
OBJCONST UCHAR OBJMEM aName0x1A00[] = "Transmit PDO 1 Mapping\000PDO 1 Mapping for a process data variable 1\000PDO 1 Mapping for a process data variable 2\000PDO 1 Mapping for a process data variable 3\000PDO 1 Mapping for a process data variable 4\000PDO 1 Mapping for a process data variable 5\000PDO 1 Mapping for a process data variable 6\000PDO 1 Mapping for a process data variable 7\000PDO 1 Mapping for a process data variable 8\000\377";

/** \brief Object 0x1A01 (Transmit PDO 2 Mapping) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x1A01[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x08 */
};
OBJCONST UCHAR OBJMEM aName0x1A01[] = "Transmit PDO 2 Mapping\000PDO 2 Mapping for a process data variable 1\000PDO 2 Mapping for a process data variable 2\000PDO 2 Mapping for a process data variable 3\000PDO 2 Mapping for a process data variable 4\000PDO 2 Mapping for a process data variable 5\000PDO 2 Mapping for a process data variable 6\000PDO 2 Mapping for a process data variable 7\000PDO 2 Mapping for a process data variable 8\000\377";

/** \brief Object 0x1A02 (Transmit PDO 3 Mapping) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x1A02[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x08 */
};
OBJCONST UCHAR OBJMEM aName0x1A02[] = "Transmit PDO 3 Mapping\000PDO 3 Mapping for a process data variable 1\000PDO 3 Mapping for a process data variable 2\000PDO 3 Mapping for a process data variable 3\000PDO 3 Mapping for a process data variable 4\000PDO 3 Mapping for a process data variable 5\000PDO 3 Mapping for a process data variable 6\000PDO 3 Mapping for a process data variable 7\000PDO 3 Mapping for a process data variable 8\000\377";

/** \brief Object 0x1A03 (Transmit PDO 4 Mapping) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x1A03[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READWRITE}, /* SubIndex 0x08 */
};
OBJCONST UCHAR OBJMEM aName0x1A03[] = "Transmit PDO 4 Mapping\000PDO 4 Mapping for a process data variable 1\000PDO 4 Mapping for a process data variable 2\000PDO 4 Mapping for a process data variable 3\000PDO 4 Mapping for a process data variable 4\000PDO 4 Mapping for a process data variable 5\000PDO 4 Mapping for a process data variable 6\000PDO 4 Mapping for a process data variable 7\000PDO 4 Mapping for a process data variable 8\000\377";

/* END GENERATED EDS PDO DESCRIPTORS */
/** @}*/

/**
 * \addtogroup CiA402Objects CiA402 Axis Objects
 * @{
 */
/* BEGIN GENERATED EDS AXIS DESCRIPTORS */
/* Generated by generate_cia402.py. Do not edit this block manually. */

/** \brief Object 0x2000 (Ridden angle) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2000 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2000[] = "Ridden angle";

/** \brief Object 0x2001 (Enable functionality) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2001 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2001[] = "Enable functionality";

/** \brief Object 0x2002 (Encoder out pulse per turn) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2002 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2002[] = "Encoder out pulse per turn";

/** \brief Object 0x2003 (12V voltage) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2003 = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2003[] = "12V voltage";

/** \brief Object 0x2004 (4V voltage) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2004 = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2004[] = "4V voltage";

/** \brief Object 0x2005 (3V3 voltage) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2005 = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2005[] = "3V3 voltage";

/** \brief Object 0x2006 (Homing current saturation) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2006 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2006[] = "Homing current saturation";

/** \brief Object 0x2007 (Homing torque saturation) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2007 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2007[] = "Homing torque saturation";

/** \brief Object 0x2008 (Homing saturation time) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2008 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2008[] = "Homing saturation time";

/** \brief Object 0x2009 (Angle offset) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2009 = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2009[] = "Angle offset";

/** \brief Object 0x200A (NFC memory manage) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x200A[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x08 */
    {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x09 */
    {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x0A */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x0B */
};
OBJCONST UCHAR OBJMEM aName0x200A[] = "NFC memory manage\000Global errors\000Password\000Commands\000Command read single object\000Value read single object\000Command write single object\000Value write single object\000Errors states canopen commands\000Memory size\000Errors history size\000Status register\000\377";

/** \brief Object 0x200B (Input output configuration) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x200B[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x08 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x09 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x0A */
};
OBJCONST UCHAR OBJMEM aName0x200B[] = "Input output configuration\000In 1\000In 2\000In 3\000In 4\000In 5\000In 6\000Out 1\000Out 2\000Input output state\000Output polarity\000\377";

/** \brief Object 0x200C (Motor constants) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x200C[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x03 */
};
OBJCONST UCHAR OBJMEM aName0x200C[] = "Motor constants\000Torque Kt\000Voltage Ke\000Used max current\000\377";

/** \brief Object 0x200D (24V voltage) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x200D = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x200D[] = "24V voltage";

/** \brief Object 0x200E (24V voltage error) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x200E = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x200E[] = "24V voltage error";

/** \brief Object 0x200F (Temperature uC) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x200F = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x200F[] = "Temperature uC";

/** \brief Object 0x2010 (Iu offset) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2010 = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2010[] = "Iu offset";

/** \brief Object 0x2011 (Iv offset) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2011 = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2011[] = "Iv offset";

/** \brief Object 0x2012 (Iw offset) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2012 = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2012[] = "Iw offset";

/** \brief Object 0x2013 (Communication error index) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2013 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2013[] = "Communication error index";

/** \brief Object 0x2014 (Warning register) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2014 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2014[] = "Warning register";

/** \brief Object 0x2015 (I2t) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x2015[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x04 */
};
OBJCONST UCHAR OBJMEM aName0x2015[] = "I2t\000Threshold current\000Threshold time\000Fault value\000Current value\000\377";

/** \brief Object 0x2016 (In out monitor) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2016 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2016[] = "In out monitor";

/** \brief Object 0x2017 (Manufacturer 01) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2017 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2017[] = "Manufacturer 01";

/** \brief Object 0x2018 (Manufacturer 02) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2018 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2018[] = "Manufacturer 02";

/** \brief Object 0x2019 (Manufacturer 03) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2019 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2019[] = "Manufacturer 03";

/** \brief Object 0x201A (Manufacturer 04) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x201A = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x201A[] = "Manufacturer 04";

/** \brief Object 0x201B (Manufacturer 05) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x201B = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x201B[] = "Manufacturer 05";

/** \brief Object 0x201C (Manufacturer 06) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x201C = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x201C[] = "Manufacturer 06";

/** \brief Object 0x201D (Manufacturer 07) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x201D = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x201D[] = "Manufacturer 07";

/** \brief Object 0x201E (Manufacturer 08) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x201E = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x201E[] = "Manufacturer 08";

/** \brief Object 0x201F (Manufacturer 09) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x201F = {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x201F[] = "Manufacturer 09";

/** \brief Object 0x2020 (Manufacturer 10) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2020 = {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2020[] = "Manufacturer 10";

/** \brief Object 0x2021 (Manufacturer 11) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2021 = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2021[] = "Manufacturer 11";

/** \brief Object 0x2022 (Manufacturer 12) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2022 = {DEFTYPE_REAL32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2022[] = "Manufacturer 12";

/** \brief Object 0x2023 (Manufacturer 13) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2023 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2023[] = "Manufacturer 13";

/** \brief Object 0x2024 (Manufacturer 14) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2024 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2024[] = "Manufacturer 14";

/** \brief Object 0x2025 (Manufacturer 15) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2025 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2025[] = "Manufacturer 15";

/** \brief Object 0x2026 (Manufacturer 16) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2026 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2026[] = "Manufacturer 16";

/** \brief Object 0x2027 (Commands) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x2027[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_BOOLEAN, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_BOOLEAN, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_BOOLEAN, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x03 */
};
OBJCONST UCHAR OBJMEM aName0x2027[] = "Commands\000Save position\000Reset microcontroller\000Start alignment routine\000\377";

/** \brief Object 0x2028 (Error field time) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x2028[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x08 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x09 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x0A */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x0B */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x0C */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x0D */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x0E */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x0F */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x10 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x11 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x12 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x13 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x14 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x15 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x16 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x17 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x18 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x19 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x1A */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x1B */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x1C */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x1D */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x1E */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x1F */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x20 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x21 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x22 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x23 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x24 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x25 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x26 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x27 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x28 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x29 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x2A */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x2B */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x2C */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x2D */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x2E */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x2F */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x30 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x31 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x32 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x33 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x34 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x35 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x36 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x37 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x38 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x39 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x3A */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x3B */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x3C */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x3D */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x3E */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x3F */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x40 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x41 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x42 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x43 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x44 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x45 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x46 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x47 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x48 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x49 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x4A */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x4B */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x4C */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x4D */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x4E */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x4F */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x50 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x51 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x52 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x53 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x54 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x55 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x56 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x57 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x58 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x59 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x5A */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x5B */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x5C */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x5D */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x5E */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x5F */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x60 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x61 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x62 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x63 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x64 */
};
OBJCONST UCHAR OBJMEM aName0x2028[] = "Error field time\000Error field time 1\000Error field time 2\000Error field time 3\000Error field time 4\000Error field time 5\000Error field time 6\000Error field time 7\000Error field time 8\000Error field time 9\000Error field time 10\000Error field time 11\000Error field time 12\000Error field time 13\000Error field time 14\000Error field time 15\000Error field time 16\000Error field time 17\000Error field time 18\000Error field time 19\000Error field time 20\000Error field time 21\000Error field time 22\000Error field time 23\000Error field time 24\000Error field time 25\000Error field time 26\000Error field time 27\000Error field time 28\000Error field time 29\000Error field time 30\000Error field time 31\000Error field time 32\000Error field time 33\000Error field time 34\000Error field time 35\000Error field time 36\000Error field time 37\000Error field time 38\000Error field time 39\000Error field time 40\000Error field time 41\000Error field time 42\000Error field time 43\000Error field time 44\000Error field time 45\000Error field time 46\000Error field time 47\000Error field time 48\000Error field time 49\000Error field time 50\000Error field time 51\000Error field time 52\000Error field time 53\000Error field time 54\000Error field time 55\000Error field time 56\000Error field time 57\000Error field time 58\000Error field time 59\000Error field time 60\000Error field time 61\000Error field time 62\000Error field time 63\000Error field time 64\000Error field time 65\000Error field time 66\000Error field time 67\000Error field time 68\000Error field time 69\000Error field time 70\000Error field time 71\000Error field time 72\000Error field time 73\000Error field time 74\000Error field time 75\000Error field time 76\000Error field time 77\000Error field time 78\000Error field time 79\000Error field time 80\000Error field time 81\000Error field time 82\000Error field time 83\000Error field time 84\000Error field time 85\000Error field time 86\000Error field time 87\000Error field time 88\000Error field time 89\000Error field time 90\000Error field time 91\000Error field time 92\000Error field time 93\000Error field time 94\000Error field time 95\000Error field time 96\000Error field time 97\000Error field time 98\000Error field time 99\000Error field time 100\000\377";

/** \brief Object 0x2029 (Current time) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x2029 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x2029[] = "Current time";

/** \brief Object 0x202A (Sensor to reference distance) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x202A = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x202A[] = "Sensor to reference distance";

/** \brief Object 0x202B (VDC Power Limits) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x202B[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x04 */
};
OBJCONST UCHAR OBJMEM aName0x202B[] = "VDC Power Limits\000VDC Power Undervoltage Threshold\000VDC Power Undervoltage Hysteresis\000VDC Power Overvoltage Threshold\000VDC Power Overvoltage Hysteresis\000\377";

/** \brief Object 0x202D (Manufacturer 17) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x202D[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x05 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x06 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x07 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x08 */
};
OBJCONST UCHAR OBJMEM aName0x202D[] = "Manufacturer 17\000Manufacturer 17 1\000Manufacturer 17 2\000Manufacturer 17 3\000Manufacturer 17 4\000Manufacturer 17 5\000Manufacturer 17 6\000Manufacturer 17 7\000Manufacturer 17 8\000\377";

/** \brief Object 0x603F (Error code) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x603F = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x603F[] = "Error code";

/** \brief Object 0x6040 (Controlword) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6040 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6040[] = "Controlword";

/** \brief Object 0x6041 (Statusword) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6041 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6041[] = "Statusword";

/** \brief Object 0x605A (Quick stop option code) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x605A = {DEFTYPE_INTEGER16, 0x10, ACCESS_READWRITE};
OBJCONST UCHAR OBJMEM aName0x605A[] = "Quick stop option code";

/** \brief Object 0x605B (Shutdown option code) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x605B = {DEFTYPE_INTEGER16, 0x10, ACCESS_READWRITE};
OBJCONST UCHAR OBJMEM aName0x605B[] = "Shutdown option code";

/** \brief Object 0x605C (Disable Operation Option Code) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x605C = {DEFTYPE_INTEGER16, 0x10, ACCESS_READWRITE};
OBJCONST UCHAR OBJMEM aName0x605C[] = "Disable Operation Option Code";

/** \brief Object 0x605D (Halt option code) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x605D = {DEFTYPE_INTEGER16, 0x10, ACCESS_READWRITE};
OBJCONST UCHAR OBJMEM aName0x605D[] = "Halt option code";

/** \brief Object 0x605E (Fault reaction option code) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x605E = {DEFTYPE_INTEGER16, 0x10, ACCESS_READWRITE};
OBJCONST UCHAR OBJMEM aName0x605E[] = "Fault reaction option code";

/** \brief Object 0x6060 (Modes of operation) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6060 = {DEFTYPE_INTEGER8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6060[] = "Modes of operation";

/** \brief Object 0x6061 (Modes of operation display) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6061 = {DEFTYPE_INTEGER8, 0x08, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6061[] = "Modes of operation display";

/** \brief Object 0x6062 (Position demand value) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6062 = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6062[] = "Position demand value";

/** \brief Object 0x6063 (Position actual internal value) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6063 = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6063[] = "Position actual internal value";

/** \brief Object 0x6064 (Position actual value) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6064 = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6064[] = "Position actual value";

/** \brief Object 0x6065 (Following error window) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6065 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6065[] = "Following error window";

/** \brief Object 0x6066 (Following error time out) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6066 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6066[] = "Following error time out";

/** \brief Object 0x6067 (Position window) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6067 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6067[] = "Position window";

/** \brief Object 0x6068 (Position window time) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6068 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6068[] = "Position window time";

/** \brief Object 0x606B (Velocity demand value) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x606B = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x606B[] = "Velocity demand value";

/** \brief Object 0x606C (Velocity actual value) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x606C = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x606C[] = "Velocity actual value";

/** \brief Object 0x606D (Velocity window) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x606D = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x606D[] = "Velocity window";

/** \brief Object 0x606E (Velocity window time) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x606E = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x606E[] = "Velocity window time";

/** \brief Object 0x606F (Velocity threshold) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x606F = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x606F[] = "Velocity threshold";

/** \brief Object 0x6070 (Velocity threshold time) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6070 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6070[] = "Velocity threshold time";

/** \brief Object 0x6071 (Target torque) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6071 = {DEFTYPE_INTEGER16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6071[] = "Target torque";

/** \brief Object 0x6072 (Max torque) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6072 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6072[] = "Max torque";

/** \brief Object 0x6073 (Max current) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6073 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6073[] = "Max current";

/** \brief Object 0x6074 (Torque demand) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6074 = {DEFTYPE_INTEGER16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6074[] = "Torque demand";

/** \brief Object 0x6075 (Motor rated current) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6075 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6075[] = "Motor rated current";

/** \brief Object 0x6076 (Motor rated torque) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6076 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6076[] = "Motor rated torque";

/** \brief Object 0x6077 (Torque actual value) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6077 = {DEFTYPE_INTEGER16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6077[] = "Torque actual value";

/** \brief Object 0x6078 (Current actual value) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6078 = {DEFTYPE_INTEGER16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6078[] = "Current actual value";

/** \brief Object 0x6079 (DC link circuit voltage) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6079 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6079[] = "DC link circuit voltage";

/** \brief Object 0x607A (Target position) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x607A = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x607A[] = "Target position";

/** \brief Object 0x607C (Home offset) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x607C = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x607C[] = "Home offset";

/** \brief Object 0x607D (Software position limit) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x607D[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
};
OBJCONST UCHAR OBJMEM aName0x607D[] = "Software position limit\000Minimal position limit\000Maximal position limit\000\377";

/** \brief Object 0x607E (Polarity) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x607E = {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x607E[] = "Polarity";

/** \brief Object 0x607F (Maximal profile velocity) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x607F = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x607F[] = "Maximal profile velocity";

/** \brief Object 0x6080 (Max motor speed) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6080 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6080[] = "Max motor speed";

/** \brief Object 0x6081 (Profile velocity) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6081 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6081[] = "Profile velocity";

/** \brief Object 0x6083 (Profile acceleration) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6083 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6083[] = "Profile acceleration";

/** \brief Object 0x6084 (Profile deceleration) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6084 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6084[] = "Profile deceleration";

/** \brief Object 0x6085 (Quick stop deceleration) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6085 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6085[] = "Quick stop deceleration";

/** \brief Object 0x6086 (Motion profile type) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6086 = {DEFTYPE_INTEGER16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6086[] = "Motion profile type";

/** \brief Object 0x6087 (Torque slope) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6087 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6087[] = "Torque slope";

/** \brief Object 0x6091 (Gear ratio) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x6091[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
};
OBJCONST UCHAR OBJMEM aName0x6091[] = "Gear ratio\000Motor revolutions\000Shaft revolutions\000\377";

/** \brief Object 0x6092 (Feed constant) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x6092[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
};
OBJCONST UCHAR OBJMEM aName0x6092[] = "Feed constant\000feed\000driving shaft revolutions\000\377";

/** \brief Object 0x6098 (Homing method) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6098 = {DEFTYPE_INTEGER8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6098[] = "Homing method";

/** \brief Object 0x6099 (Homing speeds) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x6099[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
};
OBJCONST UCHAR OBJMEM aName0x6099[] = "Homing speeds\000Speed for switch search\000Speed for zero search\000\377";

/** \brief Object 0x609A (Homing acceleration) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x609A = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x609A[] = "Homing acceleration";

/** \brief Object 0x60C0 (Interpolation sub mode select) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x60C0 = {DEFTYPE_INTEGER16, 0x10, ACCESS_READWRITE};
OBJCONST UCHAR OBJMEM aName0x60C0[] = "Interpolation sub mode select";

/** \brief Object 0x60C1 (Interpolation data record) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x60C1[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x03 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x04 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x05 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x06 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x07 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x08 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x09 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x0A */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x0B */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x0C */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x0D */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x0E */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x0F */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x10 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x11 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x12 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x13 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x14 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x15 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x16 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x17 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x18 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x19 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x1A */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x1B */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x1C */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x1D */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x1E */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x1F */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x20 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x21 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x22 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x23 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x24 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x25 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x26 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x27 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x28 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x29 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x2A */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x2B */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x2C */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x2D */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x2E */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x2F */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x30 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x31 */
    {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x32 */
};
OBJCONST UCHAR OBJMEM aName0x60C1[] = "Interpolation data record\0001st set-point\0002nd set-point\0003rd set-point\0004th set-point\0005th set-point\0006th set-point\0007th set-point\0008th set-point\0009th set-point\00010th set-point\00011th set-point\00012th set-point\00013th set-point\00014th set-point\00015th set-point\00016th set-point\00017th set-point\00018th set-point\00019th set-point\00020th set-point\00021th set-point\00022th set-point\00023th set-point\00024th set-point\00025th set-point\00026th set-point\00027th set-point\00028th set-point\00029th set-point\00030th set-point\00031th set-point\00032th set-point\00033th set-point\00034th set-point\00035th set-point\00036th set-point\00037th set-point\00038th set-point\00039th set-point\00040th set-point\00041th set-point\00042th set-point\00043th set-point\00044th set-point\00045th set-point\00046th set-point\00047th set-point\00048th set-point\00049th set-point\00050th set-point\000\377";

/** \brief Object 0x60C2 (Interpolation time period) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x60C2[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x02 */
};
OBJCONST UCHAR OBJMEM aName0x60C2[] = "Interpolation time period\000Maximum buffer size\000Interpolation time index\000\377";

/** \brief Object 0x60C4 (Interpolation data configuration) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x60C4[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READWRITE}, /* SubIndex 0x00 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_BOOLEAN, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x03 */
    {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x04 */
    {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x05 */
    {DEFTYPE_BOOLEAN, 0x08, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x06 */
};
OBJCONST UCHAR OBJMEM aName0x60C4[] = "Interpolation data configuration\000Maximum buffer size\000Actual buffer size\000Buffer organisation\000Buffer position\000Size of data record\000Buffer clear\000\377";

/** \brief Object 0x60C5 (Max acceleration) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x60C5 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x60C5[] = "Max acceleration";

/** \brief Object 0x60C6 (Max deceleration) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x60C6 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x60C6[] = "Max deceleration";

/** \brief Object 0x60F6 (Current control parameter set) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x60F6[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
};
OBJCONST UCHAR OBJMEM aName0x60F6[] = "Current control parameter set\000Current regulator P-gain\000Current regulator I-gain\000\377";

/** \brief Object 0x60F9 (Velocity control parameter set) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x60F9[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
};
OBJCONST UCHAR OBJMEM aName0x60F9[] = "Velocity control parameter set\000Velocity regulator P-gain\000Velocity regulator I-gain\000\377";

/** \brief Object 0x60FB (Position control parameter set) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x60FB[] =
{
    {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ}, /* SubIndex 0x00 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x01 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x02 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x03 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x04 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x05 */
    {DEFTYPE_REAL32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)}, /* SubIndex 0x06 */
};
OBJCONST UCHAR OBJMEM aName0x60FB[] = "Position control parameter set\000Position regulator P-gain\000Position regulator I-gain\000Position regulator D-gain\000Velocity feed forward factor\000Inertia feed forward factor\000Viscous friction feed forward factor\000\377";

/** \brief Object 0x60FF (Target velocity) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x60FF = {DEFTYPE_INTEGER32, 0x20, (ACCESS_READWRITE | OBJACCESS_RXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x60FF[] = "Target velocity";

/** \brief Object 0x6402 (Motor type) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6402 = {DEFTYPE_UNSIGNED16, 0x10, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6402[] = "Motor type";

/** \brief Object 0x6502 (Supported drive modes) descriptors. */
OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x6502 = {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ | OBJACCESS_TXPDOMAPPING)};
OBJCONST UCHAR OBJMEM aName0x6502[] = "Supported drive modes";

/* END GENERATED EDS AXIS DESCRIPTORS */
/** @}*/


/**
 * \addtogroup DeviceParaObjects Device Parameter Objects
 * @{
 */
/** 
 * \brief Object 0xF000 (Modular Device Profile) entry description
 *
 * Subindex 000 <br>
 * SubIndex 001: Module index distance<br>
 * SubIndex 002: Maximum number of modules
 */
OBJCONST TSDOINFOENTRYDESC    OBJMEM asEntryDesc0xF000[3] = {
   {DEFTYPE_UNSIGNED8, 0x8, ACCESS_READ },
   {DEFTYPE_UNSIGNED16, 0x10, ACCESS_READ},
   {DEFTYPE_UNSIGNED16, 0x10, ACCESS_READ}};

/** \brief Object 0xF000 (Modular Device Profile) object and entry names*/
OBJCONST UCHAR OBJMEM aName0xF000[] = "Modular Device Profile\000Index distance\000Maximum number of modules\000\377";


/** 
 * \brief 0xF010 (Module profile list) entry descriptions
 *
 * Subindex 0<br>
 * SubIndex x
 * (x > 0)
 */
OBJCONST TSDOINFOENTRYDESC    OBJMEM asEntryDesc0xF010[3] = {
   {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ},
   {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READ},
   {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READ}};

/**
 * \brief 0xF010 (Module profile list) object name
 *
 * no entry names defined because the object is an array (for every entry > 0 "SubIndex xxx" is returned)
 */   
OBJCONST UCHAR OBJMEM aName0xF010[] = "Module Profile List";


/** 
 * \brief 0xF030 (Configured Modules Ident) entry descriptions
 *
 * Subindex 0<br>
 * SubIndex x
 * (x > 0)
 */
OBJCONST TSDOINFOENTRYDESC    OBJMEM asEntryDesc0xF030[] = {
   {DEFTYPE_UNSIGNED8, 0x08, (ACCESS_READ|ACCESS_WRITE_PREOP)},
   {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ|ACCESS_WRITE_PREOP)},
   {DEFTYPE_UNSIGNED32, 0x20, (ACCESS_READ|ACCESS_WRITE_PREOP)}};

/**
 * \brief 0xF030 (Configured Modules Ident) object name
 *
 * no entry names defined because the object is an array (for every entry > 0 "SubIndex xxx" is returned)
 */    
OBJCONST UCHAR OBJMEM aName0xF030[] = "Configured Module Ident List";


/** 
 * \brief 0xF050 (Module detected list) entry descriptions
 *
 * Subindex 0<br>
 * SubIndex x
 * (x > 0)
 */
OBJCONST TSDOINFOENTRYDESC    OBJMEM asEntryDesc0xF050[] = {
   {DEFTYPE_UNSIGNED8, 0x08, ACCESS_READ},
   {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READ},
   {DEFTYPE_UNSIGNED32, 0x20, ACCESS_READ}};

   
/**
 * \brief 0xF050 (Module detected list) object name
 *
 * no entry names defined because the object is an array (for every entry > 0 "SubIndex xxx" is returned)
 */       
OBJCONST UCHAR OBJMEM aName0xF050[] = "Module detected list";
/** @}*/
#endif


/**
 * \addtogroup SmAssignObjects SyncManager Assignment Objects
 * @{
 */

/**
 * \brief 0x1C12 (SyncManager 2 assignment) variable to handle object data
 * 
 * SubIndex 0 : 1<br>
 * SubIndex 1 : 0x1602
 * SubIndex 2 : 0
 */
PROTO TOBJ1C12 sRxPDOassign
#ifdef _CiA402_
= {1,{0x1600}}
#endif
;


/**
 * \brief 0x1C13 (SyncManager 3 assignment) variable to handle object data
 * 
 * SubIndex 0 : 1<br>
 * SubIndex 1 : 0x1A02<br>
 * SubIndex 2 : 0
 */
PROTO TOBJ1C13 sTxPDOassign
#ifdef _CiA402_
= {1,{0x1A00}}
#endif
;
/** @}*/


/**
 * \addtogroup DeviceParaObjects Device Parameter Objects
 * @{
 */
/** 
 * \brief Object 0xF000 (Modular Device Profile) variable to handle object data
 *
 * SubIndex 0 : 2<br>
 * SubIndex 1 : 0x800 (index distance)<br>
 * SubIndex 2 : MAX_AXES (number of modules depends on the number of axes)
 */
PROTO TOBJF000 sModulardeviceprofile
#ifdef _CiA402_
= {2, 0x800, MAX_AXES}
#endif
;


/** 
 * \brief Object 0xF010 (Module profile list) variable to handle object data
 *
 * SubIndex 0 : 1<br>
 * SubIndex 1 :2 (Low Word)<br>
 * SubIndex 2 : 0
 */
PROTO TOBJF010 sModuleProfileInfo
#ifdef _CiA402_
= {1,{2}}
#endif
;

/** 
 * \brief Object 0xF030 (Configured Module List) variable to handle object data
 *
 * SubIndex 0 : 1<br>
 * SubIndex 1 : csv Module is set by default<br>
 * SubIndex 2 : 0
 */
PROTO TOBJF030 sConfiguredModuleIdentList
#ifdef _CiA402_
= {1,{0x319800}}
#endif
;

PROTO UINT8 Write0xF030( UINT16 index, UINT8 subindex, UINT32 dataSize, UINT16 MBXMEM * pData, UINT8 bCompleteAccess );


/** 
 * \brief Object 0xF050 (Detected Module List) variable to handle object data
 *
 * SubIndex 0 : 1<br>
 * SubIndex 1 : csv Module is set by default<br>
 * SubIndex 2 : 0
 */
PROTO TOBJF050 sDetectedModuleIdentList
#ifdef _CiA402_
= {1,{0x319800}}
#endif
;
/** @}*/


/**
 * \addtogroup CiA402Objects CiA402 Axis Objects
 * @{
 */
/** \brief Axis object default values generated from the EDS. */
PROTO CiA402Objects DefCiA402ObjectValues
#ifdef _CiA402_
=
{
    {3, {0x60400010, 0x607A0020, 0x60600008, 0, 0, 0, 0, 0}}, /* 0x1600 Receive PDO 1 Mapping */
    {0, {0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x1601 Receive PDO 2 Mapping */
    {0, {0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x1602 Receive PDO 3 Mapping */
    {0, {0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x1603 Receive PDO 4 Mapping */
    {3, {0x60410010, 0x60640020, 0x60610008, 0, 0, 0, 0, 0}}, /* 0x1A00 Transmit PDO 1 Mapping */
    {0, {0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x1A01 Transmit PDO 2 Mapping */
    {0, {0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x1A02 Transmit PDO 3 Mapping */
    {0, {0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x1A03 Transmit PDO 4 Mapping */
    0, /* 0x2000 Ridden angle */
    0, /* 0x2001 Enable functionality */
    0, /* 0x2002 Encoder out pulse per turn */
    0.0F, /* 0x2003 12V voltage */
    0.0F, /* 0x2004 4V voltage */
    0.0F, /* 0x2005 3V3 voltage */
    0, /* 0x2006 Homing current saturation */
    0, /* 0x2007 Homing torque saturation */
    0, /* 0x2008 Homing saturation time */
    0.0F, /* 0x2009 Angle offset */
    {11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}, /* 0x200A NFC memory manage */
    {10, {0, 0, 0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x200B Input output configuration */
    {3, {0.0F, 0.0F, 0.0F}}, /* 0x200C Motor constants */
    0.0F, /* 0x200D 24V voltage */
    0.0F, /* 0x200E 24V voltage error */
    0.0F, /* 0x200F Temperature uC */
    0.0F, /* 0x2010 Iu offset */
    0.0F, /* 0x2011 Iv offset */
    0.0F, /* 0x2012 Iw offset */
    0, /* 0x2013 Communication error index */
    0, /* 0x2014 Warning register */
    {4, 0, 0, 0, 0}, /* 0x2015 I2t */
    0, /* 0x2016 In out monitor */
    0, /* 0x2017 Manufacturer 01 */
    0, /* 0x2018 Manufacturer 02 */
    0, /* 0x2019 Manufacturer 03 */
    0, /* 0x201A Manufacturer 04 */
    0, /* 0x201B Manufacturer 05 */
    0, /* 0x201C Manufacturer 06 */
    0, /* 0x201D Manufacturer 07 */
    0, /* 0x201E Manufacturer 08 */
    0.0F, /* 0x201F Manufacturer 09 */
    0.0F, /* 0x2020 Manufacturer 10 */
    0.0F, /* 0x2021 Manufacturer 11 */
    0.0F, /* 0x2022 Manufacturer 12 */
    0, /* 0x2023 Manufacturer 13 */
    0, /* 0x2024 Manufacturer 14 */
    0, /* 0x2025 Manufacturer 15 */
    0, /* 0x2026 Manufacturer 16 */
    {3, {0, 0, 0}}, /* 0x2027 Commands */
    {100, {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x2028 Error field time */
    0, /* 0x2029 Current time */
    0, /* 0x202A Sensor to reference distance */
    {4, {400, 50, 550, 50}}, /* 0x202B VDC Power Limits */
    {8, {0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x202D Manufacturer 17 */
    0, /* 0x603F Error code */
    0, /* 0x6040 Controlword */
    0, /* 0x6041 Statusword */
    2, /* 0x605A Quick stop option code */
    0, /* 0x605B Shutdown option code */
    SLOW_DOWN_RAMP, /* 0x605C Disable Operation Option Code */
    0, /* 0x605D Halt option code */
    QUICKSTOP_RAMP, /* 0x605E Fault reaction option code */
    0, /* 0x6060 Modes of operation */
    0, /* 0x6061 Modes of operation display */
    0, /* 0x6062 Position demand value */
    0, /* 0x6063 Position actual internal value */
    0, /* 0x6064 Position actual value */
    0, /* 0x6065 Following error window */
    0, /* 0x6066 Following error time out */
    0, /* 0x6067 Position window */
    0, /* 0x6068 Position window time */
    0, /* 0x606B Velocity demand value */
    0, /* 0x606C Velocity actual value */
    0, /* 0x606D Velocity window */
    0, /* 0x606E Velocity window time */
    0, /* 0x606F Velocity threshold */
    0, /* 0x6070 Velocity threshold time */
    0, /* 0x6071 Target torque */
    0, /* 0x6072 Max torque */
    0, /* 0x6073 Max current */
    0, /* 0x6074 Torque demand */
    0, /* 0x6075 Motor rated current */
    0, /* 0x6076 Motor rated torque */
    0, /* 0x6077 Torque actual value */
    0, /* 0x6078 Current actual value */
    0, /* 0x6079 DC link circuit voltage */
    0, /* 0x607A Target position */
    0, /* 0x607C Home offset */
    {2, 0x88CA6C00, 0x77359400}, /* 0x607D Software position limit */
    0, /* 0x607E Polarity */
    0, /* 0x607F Maximal profile velocity */
    0, /* 0x6080 Max motor speed */
    0, /* 0x6081 Profile velocity */
    0, /* 0x6083 Profile acceleration */
    0, /* 0x6084 Profile deceleration */
    0, /* 0x6085 Quick stop deceleration */
    0, /* 0x6086 Motion profile type */
    0, /* 0x6087 Torque slope */
    {2, {0, 0}}, /* 0x6091 Gear ratio */
    {2, {0, 0}}, /* 0x6092 Feed constant */
    0, /* 0x6098 Homing method */
    {2, {0, 0}}, /* 0x6099 Homing speeds */
    0, /* 0x609A Homing acceleration */
    0, /* 0x60C0 Interpolation sub mode select */
    {50, {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}}, /* 0x60C1 Interpolation data record */
    {2, 1, -3}, /* 0x60C2 Interpolation time period */
    {6, 0, 0, 0, 0, 0, 1}, /* 0x60C4 Interpolation data configuration */
    0, /* 0x60C5 Max acceleration */
    0, /* 0x60C6 Max deceleration */
    {2, {0.0F, 0.0F}}, /* 0x60F6 Current control parameter set */
    {2, {0.0F, 0.0F}}, /* 0x60F9 Velocity control parameter set */
    {6, {0.0F, 0.0F, 0.0F, 0.0F, 0.0F, 0.0F}}, /* 0x60FB Position control parameter set */
    0, /* 0x60FF Target velocity */
    10, /* 0x6402 Motor type */
    0 /* 0x6502 Supported drive modes */
}
#endif
;
/** @}*/


/**
 *\brief Base CiA402 device object dictionary
 */
PROTO TOBJECT    OBJMEM ApplicationObjDic[]
#ifdef _CiA402_
= {/* Object 0x1C12 */
   {NULL,NULL, 0x1C12, {DEFTYPE_UNSIGNED16, MAX_AXES | (OBJCODE_ARR << 8)}, asPDOAssignEntryDesc, aName0x1C12, &sRxPDOassign, NULL, NULL, 0x0000 },
   /* Object 0x1C13 */
   {NULL,NULL, 0x1C13, {DEFTYPE_UNSIGNED16, MAX_AXES | (OBJCODE_ARR << 8)}, asPDOAssignEntryDesc, aName0x1C13, &sTxPDOassign, NULL, NULL, 0x0000 },
    /* Object 0xF000 */
   {NULL,NULL,   0xF000, {DEFTYPE_RECORD, 2 | (OBJCODE_REC << 8)}, asEntryDesc0xF000, aName0xF000, &sModulardeviceprofile, NULL, NULL, 0x0000 },
    /* Object 0xF010 */
   {NULL,NULL,   0xF010, {DEFTYPE_UNSIGNED32, MAX_AXES | (OBJCODE_ARR << 8)}, asEntryDesc0xF010, aName0xF010, &sModuleProfileInfo, NULL, NULL, 0x0000 },
    /* Object 0xF030 */
   {NULL,NULL,   0xF030, {DEFTYPE_UNSIGNED32, MAX_AXES | (OBJCODE_ARR << 8)}, asEntryDesc0xF030, aName0xF030, &sConfiguredModuleIdentList, NULL, Write0xF030, 0x0000 },
   /* Object 0xF050 */
   {NULL,NULL, 0xF050, {DEFTYPE_UNSIGNED32, MAX_AXES | (OBJCODE_ARR << 8)}, asEntryDesc0xF050, aName0xF050, &sDetectedModuleIdentList, NULL, NULL, 0x0000 },
   {NULL,NULL, 0xFFFF, {0, 0}, NULL, NULL, NULL, NULL, NULL, 0x000}}
#endif
;



/** \brief Object dictionary related to one CiA402 axis. */
PROTO TOBJECT OBJMEM DefCiA402AxisObjDic[]
#ifdef _CiA402_
=
{
    {NULL, NULL, 0x1600, {DEFTYPE_PDOMAPPING, 8 | (OBJCODE_REC << 8)}, asEntryDesc0x1600, aName0x1600, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x1601, {DEFTYPE_PDOMAPPING, 8 | (OBJCODE_REC << 8)}, asEntryDesc0x1601, aName0x1601, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x1602, {DEFTYPE_PDOMAPPING, 8 | (OBJCODE_REC << 8)}, asEntryDesc0x1602, aName0x1602, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x1603, {DEFTYPE_PDOMAPPING, 8 | (OBJCODE_REC << 8)}, asEntryDesc0x1603, aName0x1603, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x1A00, {DEFTYPE_PDOMAPPING, 8 | (OBJCODE_REC << 8)}, asEntryDesc0x1A00, aName0x1A00, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x1A01, {DEFTYPE_PDOMAPPING, 8 | (OBJCODE_REC << 8)}, asEntryDesc0x1A01, aName0x1A01, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x1A02, {DEFTYPE_PDOMAPPING, 8 | (OBJCODE_REC << 8)}, asEntryDesc0x1A02, aName0x1A02, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x1A03, {DEFTYPE_PDOMAPPING, 8 | (OBJCODE_REC << 8)}, asEntryDesc0x1A03, aName0x1A03, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2000, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2000, aName0x2000, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2001, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2001, aName0x2001, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2002, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2002, aName0x2002, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2003, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2003, aName0x2003, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2004, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2004, aName0x2004, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2005, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2005, aName0x2005, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2006, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2006, aName0x2006, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2007, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2007, aName0x2007, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2008, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2008, aName0x2008, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2009, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2009, aName0x2009, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x200A, {DEFTYPE_RECORD, 11 | (OBJCODE_REC << 8)}, asEntryDesc0x200A, aName0x200A, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x200B, {DEFTYPE_RECORD, 10 | (OBJCODE_REC << 8)}, asEntryDesc0x200B, aName0x200B, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x200C, {DEFTYPE_RECORD, 3 | (OBJCODE_REC << 8)}, asEntryDesc0x200C, aName0x200C, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x200D, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x200D, aName0x200D, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x200E, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x200E, aName0x200E, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x200F, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x200F, aName0x200F, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2010, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2010, aName0x2010, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2011, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2011, aName0x2011, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2012, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2012, aName0x2012, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2013, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2013, aName0x2013, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2014, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2014, aName0x2014, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2015, {DEFTYPE_RECORD, 4 | (OBJCODE_REC << 8)}, asEntryDesc0x2015, aName0x2015, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2016, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2016, aName0x2016, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2017, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2017, aName0x2017, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2018, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2018, aName0x2018, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2019, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2019, aName0x2019, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x201A, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x201A, aName0x201A, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x201B, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x201B, aName0x201B, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x201C, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x201C, aName0x201C, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x201D, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x201D, aName0x201D, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x201E, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x201E, aName0x201E, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x201F, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x201F, aName0x201F, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2020, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2020, aName0x2020, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2021, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2021, aName0x2021, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2022, {DEFTYPE_REAL32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2022, aName0x2022, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2023, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2023, aName0x2023, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2024, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2024, aName0x2024, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2025, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2025, aName0x2025, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2026, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2026, aName0x2026, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2027, {DEFTYPE_RECORD, 3 | (OBJCODE_REC << 8)}, asEntryDesc0x2027, aName0x2027, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2028, {DEFTYPE_UNSIGNED32, 100 | (OBJCODE_ARR << 8)}, asEntryDesc0x2028, aName0x2028, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x2029, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x2029, aName0x2029, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x202A, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x202A, aName0x202A, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x202B, {DEFTYPE_RECORD, 4 | (OBJCODE_REC << 8)}, asEntryDesc0x202B, aName0x202B, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x202D, {DEFTYPE_UNSIGNED32, 8 | (OBJCODE_ARR << 8)}, asEntryDesc0x202D, aName0x202D, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x603F, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x603F, aName0x603F, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6040, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6040, aName0x6040, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6041, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6041, aName0x6041, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x605A, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x605A, aName0x605A, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x605B, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x605B, aName0x605B, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x605C, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x605C, aName0x605C, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x605D, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x605D, aName0x605D, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x605E, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x605E, aName0x605E, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6060, {DEFTYPE_INTEGER8, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6060, aName0x6060, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6061, {DEFTYPE_INTEGER8, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6061, aName0x6061, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6062, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6062, aName0x6062, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6063, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6063, aName0x6063, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6064, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6064, aName0x6064, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6065, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6065, aName0x6065, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6066, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6066, aName0x6066, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6067, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6067, aName0x6067, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6068, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6068, aName0x6068, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x606B, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x606B, aName0x606B, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x606C, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x606C, aName0x606C, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x606D, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x606D, aName0x606D, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x606E, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x606E, aName0x606E, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x606F, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x606F, aName0x606F, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6070, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6070, aName0x6070, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6071, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6071, aName0x6071, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6072, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6072, aName0x6072, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6073, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6073, aName0x6073, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6074, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6074, aName0x6074, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6075, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6075, aName0x6075, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6076, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6076, aName0x6076, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6077, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6077, aName0x6077, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6078, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6078, aName0x6078, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6079, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6079, aName0x6079, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x607A, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x607A, aName0x607A, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x607C, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x607C, aName0x607C, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x607D, {DEFTYPE_RECORD, 2 | (OBJCODE_REC << 8)}, asEntryDesc0x607D, aName0x607D, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x607E, {DEFTYPE_UNSIGNED8, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x607E, aName0x607E, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x607F, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x607F, aName0x607F, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6080, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6080, aName0x6080, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6081, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6081, aName0x6081, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6083, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6083, aName0x6083, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6084, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6084, aName0x6084, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6085, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6085, aName0x6085, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6086, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6086, aName0x6086, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6087, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6087, aName0x6087, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6091, {DEFTYPE_RECORD, 2 | (OBJCODE_REC << 8)}, asEntryDesc0x6091, aName0x6091, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6092, {DEFTYPE_RECORD, 2 | (OBJCODE_REC << 8)}, asEntryDesc0x6092, aName0x6092, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6098, {DEFTYPE_INTEGER8, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6098, aName0x6098, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6099, {DEFTYPE_RECORD, 2 | (OBJCODE_REC << 8)}, asEntryDesc0x6099, aName0x6099, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x609A, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x609A, aName0x609A, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60C0, {DEFTYPE_INTEGER16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x60C0, aName0x60C0, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60C1, {DEFTYPE_RECORD, 50 | (OBJCODE_REC << 8)}, asEntryDesc0x60C1, aName0x60C1, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60C2, {DEFTYPE_RECORD, 2 | (OBJCODE_REC << 8)}, asEntryDesc0x60C2, aName0x60C2, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60C4, {DEFTYPE_RECORD, 6 | (OBJCODE_REC << 8)}, asEntryDesc0x60C4, aName0x60C4, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60C5, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x60C5, aName0x60C5, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60C6, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x60C6, aName0x60C6, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60F6, {DEFTYPE_RECORD, 2 | (OBJCODE_REC << 8)}, asEntryDesc0x60F6, aName0x60F6, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60F9, {DEFTYPE_RECORD, 2 | (OBJCODE_REC << 8)}, asEntryDesc0x60F9, aName0x60F9, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60FB, {DEFTYPE_RECORD, 6 | (OBJCODE_REC << 8)}, asEntryDesc0x60FB, aName0x60FB, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x60FF, {DEFTYPE_INTEGER32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x60FF, aName0x60FF, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6402, {DEFTYPE_UNSIGNED16, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6402, aName0x6402, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0x6502, {DEFTYPE_UNSIGNED32, 0 | (OBJCODE_VAR << 8)}, &sEntryDesc0x6502, aName0x6502, NULL, NULL, NULL, 0x0000},
    {NULL, NULL, 0xFFFF, {0, 0}, NULL, NULL, NULL, NULL, NULL, 0x0000}
}
#endif
;

PROTO void APPL_Application(void);

PROTO void   APPL_AckErrorInd(UINT16 stateTrans);
PROTO UINT16 APPL_StartMailboxHandler(void);
PROTO UINT16 APPL_StopMailboxHandler(void);
PROTO UINT16 APPL_StartInputHandler(UINT16 *pIntMask);
PROTO UINT16 APPL_StopInputHandler(void);
PROTO UINT16 APPL_StartOutputHandler(void);
PROTO UINT16 APPL_StopOutputHandler(void);

PROTO UINT16 APPL_GenerateMapping(UINT16 *pInputSize,UINT16 *pOutputSize);
PROTO void APPL_InputMapping(UINT16* pData);
PROTO void APPL_OutputMapping(UINT16* pData);

PROTO void CiA402_LocalError(UINT16 ErrorCode);
PROTO void CiA402_StateMachine(void);

PROTO UINT16 CiA402_Init(void);
PROTO void CiA402_DeallocateAxis(void);

#undef PROTO
/** @}*/
