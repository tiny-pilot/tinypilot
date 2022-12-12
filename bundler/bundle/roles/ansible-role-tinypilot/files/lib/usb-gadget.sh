#!/bin/bash

# Shared parameters and functionality for the usb gadget.
# See: docs/usb-gadget-driver.md

export readonly USB_DEVICE_DIR="g1"
export readonly USB_GADGET_PATH="/sys/kernel/config/usb_gadget"
export readonly USB_DEVICE_PATH="${USB_GADGET_PATH}/${USB_DEVICE_DIR}"

export readonly USB_STRINGS_DIR="strings/0x409"
export readonly USB_KEYBOARD_FUNCTIONS_DIR="functions/hid.keyboard"
export readonly USB_MOUSE_FUNCTIONS_DIR="functions/hid.mouse"
export readonly USB_MASS_STORAGE_NAME="mass_storage.0"
export readonly USB_MASS_STORAGE_FUNCTIONS_DIR="functions/${USB_MASS_STORAGE_NAME}"

export readonly USB_CONFIG_INDEX=1
export readonly USB_CONFIG_DIR="configs/c.${USB_CONFIG_INDEX}"
export readonly USB_ALL_CONFIGS_DIR="configs/*"
export readonly USB_ALL_FUNCTIONS_DIR="functions/*"

function usb_gadget_activate {
  ls /sys/class/udc > "${USB_DEVICE_PATH}/UDC"
  chmod 777 /dev/hidg0
  chmod 777 /dev/hidg1
}
export -f usb_gadget_activate

function usb_gadget_deactivate {
  echo '' > "${USB_DEVICE_PATH}/UDC"
}
export -f usb_gadget_deactivate
