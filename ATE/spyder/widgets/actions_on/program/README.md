# Test Program Name Definition

Project_Hardware_Base_Target_Flow_Designator.py

`Project`

`Hardware`

`Base`

`Target`

`FLOW` ➜ MIR/MODE_COD
  - 'C' = Checker ➜ holds the load-board/probe-card checker/calibration program(s)

  - 'M' = Maintenance ➜ holds the program(s) the Maintenance Engineers use, thus the **MAINTENANCE department**.

  - 'P' = Production ➜ holds the programs for production mode, thus the **PRODUCTION department**.

  - 'E' = Engineering ➜ holds the programs for the Test- and Product Engineers, thus the **TEST Department**

  - 'V' = Validation ➜ hods the programs for the Design Engineers, thus the **R&D department**.

  - 'Q' = Quality ➜ holds the programs for the Quality Engineers, thus the **QUALITY department**.

  - 'q' = Qualification ➜ holds the programs for the Qualification Engineers, thus the **QUALIFICATION department**.

`Designator` ➜ MIR/FLOW_ID (possibilities depend on the `Flow`)

  | Flow | Designator       | Examples  |
  |:-----|:-----------------|:------------|
  | C    | 1, 2, 3, ...     | CTCA_HW1_FT_XYZ_C_1 ➜ Final Test, first checker program |
  | M    | 1, 2, 3, ...     | CTCA_HW1_FT_XYZ_M_1 ➜ Final Test, first maintenance program |
  | P    | 1, 2, 3, ... [QC]| CTCA_HW1_FT_XYZ_P_1 ➜ Final Test, production, first program<br> CTCA_HW1_FT_XYZ_P_QC ➜ Final Test, Production, Quality Check |
  | E    | 1, 2, 3, ...     | CTCA_HW1_FT_XYZ_E_7 ➜ Final Test, engineering program #7 |
  | V    | 1, 2, 3, ...     | CTCA_HW1_FT_XYZ_V_3 ➜ Final Test, validation program #3 |
  | Q    | 1, 2, 3, ...     | CTCA_HW1_FT_XYZ_Q_2 ➜ Final Test, quality program #2 |
  | q    | **see below**    | [reference](https://github.com/ate-org/ATE.org/blob/master/docs/Qualification_flow.xlsx) |

| q-flow | Designator | Example |
|:-------|:-----------|:--------|
| ZHM    | ZMH1, ZMH2, ... | CTCA_HW1_FT_XYZ_q_ZMH1 ➜ Qualification, **Z**ero **H**our **M**easurements #1 |
| ABSMAX | ABSMAX1, ... | CTCA_HW1_FT_XYZ_q_ABSMAX1 ➜ Qualification, **ABS**olute **MAX**imum #1 |
| EC     | EC1, EC2, ... | CTCA_HW1_FT_XYZ_q_EC1 ➜ Qualification, **E**ndurance **C**ycling #1 |
| HTOL   | **see below** | |
| HTSL   |


# HTOL
**H**igh **T**emperature **O**perating **L**ife

Here we are interested to see (in a Highley Accelerated Lifetime Test) at some 'points in time' how many devices die.
We thus need a few groups of HTOL program(s) that are infact the 'points in time'. The difference is (usually) in how many hours we accelerated the life time since a reference. The 'Designator' is thus a bit more complex than all the other cases.

HTOL1008h1 ➜ 'HTOL' + '1008h' + '1'
  - 'HTOL' is fixed
  - '1008h' is the `name` of the HTOL group
  - '1' is the sequence of the program in the HTOL group (a group with only one program has the '1' also present)

# TODO
  - [ ] Add a 'checker' flow for PR
  - [ ] Add a 'checker' flow for FT
  - [ ] add a 'maintenance' flow for PR
  - [ ] add a 'maintenance' flow for FT
  - [ ] rename 'characterisation' to 'quality' for PR
  - [ ] rename 'characterisation' to 'quality' for FT
  - [ ] make sure the flows are organized as follows (to to bottom):
    - checker
    - mainenance
    - production
    - engineering
    - validation
    - quality
    - qualification (only present for FT, as already implemented)
  - [ ] change 'Prog' into the project name for all 'Add Program' actions
  - [ ] flows/production : if only one program exists, the 'Move Up' and 'Move Down' must be disabled
  - [ ] flows/production/program : on 'Edit', Hardware, Base and Target should **not** be editable, the rest **is** editable
  - [ ] flows/engineering : if only one program exists, the 'Move Up' and 'Move Down' must be disabled
  - [ ] flows/engineering/program : on 'Edit', Hardware, Base and Target should **not** be editable, the rest **is** editable


  - [ ] set the default `USER_TXT` as follows (depending on the `Flow`)
    - [ ]  'C' = f"Checker program for {Target} in {Base} at {Temperature}"
    - [ ]  'M' = f"Maintenance program for {Target} in {Base} at {Temperature}"
    - [ ]  'P' = f"Production program #{Designator} for {Target} in {Base} at {Temperature}"
    - [ ]  'E' = f"Engineering program #{Designator} for {Target} in {Base} at {Temperature}
    - [ ]  'V' = f"Validation program #{Designator} for {Target} in {Base} at {Temperature}"
    - [ ]  'Q' = f"Quality program #{Designator} for {Target} in {Base} at {Temperature}"
    - [ ]  'q' = f"Quality program #{Designator} for {Target} in {Base} at {Temperature}"
