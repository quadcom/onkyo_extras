# Onkyo Extras

A Home Assistant custom integration for an Onkyo/Integra receiver over its
own eISCP TCP connection (port 60128). It replaces the core `onkyo`
integration: these receivers allow only one eISCP connection per client
address, so the two cannot run at the same time.

It adds:

- A media player per zone the receiver reports as present (main zone plus
  Zone 2 / Zone 3 where fitted): power, volume, mute, source select, and,
  on the main zone, sound mode select.
- Subwoofer and center channel level, front bass/treble.
- Display dimmer, dialog enhancement, late night mode.
- Cinema filter, music optimizer.
- Detailed audio/video format sensors and an HDR indicator.
- On-screen menu navigation buttons.

## Install

Add this repository to HACS as a custom repository (category:
Integration), install "Onkyo Extras", then restart Home Assistant. Remove
the core `onkyo` integration for this receiver first.

## Configure

Settings > Devices & services > Add integration > Onkyo Extras. You only
need the receiver's host (IP address or hostname); the eISCP port
defaults to 60128.

Settings > Devices & services > Onkyo Extras > Configure sets two options:

- **Maximum volume** - caps how loud `volume_set` and `volume_up` can drive
  any zone, as a percent of the receiver's own maximum.
- **Sound modes to show** - which listening modes appear in the main
  zone's sound mode list.
