# 1 · Hardware & BIOS

## Machine

Intel NUC8i5BEH (“Bean Canyon”). Relevant I/O:

- 1 × **HDMI 2.0a** → screen 1
- 1 × **USB-C / Thunderbolt 3** carrying **DisplayPort 1.2** → screens 2 + 3
  via an **MST hub** (USB-C → 2× DisplayPort). The Iris Plus 655 iGPU drives
  up to 3 independent displays.
- 1 × Gigabit Ethernet → installation LAN
- M.2 SSD (OS + database), optional 2.5" SATA bay

Buy/have on site:

- USB-C (DP alt mode) → dual DisplayPort **MST hub** (not a plain splitter —
  a splitter mirrors, MST gives independent outputs)
- Spare HDMI/DP cables one size longer than you think you need

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
- Zip-tie/strain-relieve HDMI, USB-C and power — connectors work loose over weeks
- Label both ends of every cable
