# 1 · Hardware & BIOS

## Machine

Intel NUC 11 Essential, **SWNUC11ATKC4000** (NUC11ATKC4, “Atlas Canyon”):
Celeron N4500 with Intel UHD Graphics. Relevant I/O:

- 1 × **DisplayPort** → **MST hub** → screens 1–3. The iGPU drives up to 3
  independent displays (check with the test viewer that the hub really gives
  3 separate outputs); the HDMI port is not used.
- 1 × Gigabit Ethernet → installation LAN
- M.2 SSD (OS + database), optional 2.5" SATA bay

Buy/have on site:

- 3-port DisplayPort **MST hub** (not a plain splitter — a splitter mirrors
  the same picture to every screen, MST gives independent outputs)
- Spare DP cables one size longer than you think you need

## BIOS settings (F2 at boot)

These make the machine survive unattended operation at the venue:

| Setting                              | Value                                  |
|--------------------------------------|----------------------------------------|
| Power → **After Power Failure**      | **Power On** (essential — venue staff will cut power at the mains) |
| Power → Wake on LAN from S4/S5       | Power On – Normal Boot                 |
| Boot → Boot Devices                  | M.2 SSD only, disable USB boot after install |
| Security → Secure Boot               | Optional; Debian works with it on      |
| Fan control                          | Quiet/Balanced — the NUC sits in an exhibition space |

Optionally set a BIOS supervisor password so visitors with a keyboard can't
change settings.

## Physical checklist for the venue

- Mount the NUC with airflow around the vents (not sealed in a plinth without holes)
- Zip-tie/strain-relieve DP and power — connectors work loose over weeks
- Label both ends of every cable
