# Onkyo Extras

A Home Assistant custom integration that adds the controls the core
`onkyo` integration does not expose: subwoofer and center channel level,
front bass/treble, display dimmer, dialog enhancement, late night mode,
cinema filter, music optimizer, detailed audio/video format sensors, an
HDR indicator, and on-screen menu navigation buttons.

It talks to the receiver over its own eISCP TCP connection (port 60128),
alongside the core `onkyo` integration's connection - the two run at the
same time without conflicting.

## Install

Add this repository to HACS as a custom repository (category:
Integration), install "Onkyo Extras", then restart Home Assistant.

## Configure

Settings > Devices & services > Add integration > Onkyo Extras. You only
need the receiver's host (IP address or hostname); the eISCP port
defaults to 60128.
