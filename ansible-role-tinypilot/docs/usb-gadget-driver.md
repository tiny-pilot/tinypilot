# USB Gadget Driver and `configfs`

We use `configfs` for configuring the USB gadget driver. Since `configfs` can feel unintuitive to work with, here is a quick overview of how it works, and what some of its quirks are.

See also the Linux kernel documentation:

- [General `configfs` overview](https://www.kernel.org/doc/Documentation/filesystems/configfs/configfs.txt)
- [USB gadget driver](https://www.kernel.org/doc/Documentation/usb/gadget_configfs.txt)
- [Reference of available parameters and possible values](https://www.kernel.org/doc/Documentation/ABI/testing/)

## Introduction

`configfs` is a virtual file system provided by the Linux kernel. It is mounted underneath `/sys/kernel/config/`. The file system does not map to a persistent disk, though, but the entire structure is held in memory.

The basic idea behind `configfs` is to interact with kernel functionality via file system APIs. So the file and directory entries in `configfs` are like a facade that’s directly wrapped around regular operating system APIs. Making changes to `configfs` files or folders is equivalent to making function calls (to system APIs), rather than merely persisting values on disk.

Examples for possible operations:

```bash
# Set up config for a USB mouse.
mkdir -p functions/hid.mouse

# Make mass storage behave like a CD-ROM drive.
echo 1 > functions/mass_storage.0/lun.0/cdrom
```

## Internal folder structure

The `configfs` files and folders must be in line with a specific, predefined structure.

- `/sys/kernel/config/usb_gadget/`: Contains a sub-folder per gadget configuration.
  - `g1/`: We have a single gadget registered right now, which is identified by `g1`. Among other items, this folder contains:
    - `UDC`: While the gadget is activated, this contains the name of the USB device controller (hence the acronym). If the gadget is deactivated, this file is empty. That means, the active-state of the gadget can be controlled through the value in this file.
    - `functions/`: Contains the actual configurations for the USB interface features. Creating a sub-folder (e.g. `hid.mouse` for the USB mouse) will automatically set up the internal file structure of that new folder. These functions need to be symlinked from the `configs/c.1` folder, otherwise they won’t have any effect. Example items:
      - `hid.mouse/`: USB mouse config
      - `hid.keyboard/`: USB keyboard config
      - `mass_storage.0`: USB mass storage config
    - `configs/`: This folder contains the complete and authoritative configurations for the USB gadget. There could be multiple ones, but we only use one right now, which is identified by `c.1`.
      - `c.1/`: Among others:
        - `strings/`: Device info, like the serial number or the manufacturer name.
        - `hid.mouse/`: Example of a symlink to the `functions/hid.mouse` folder. It only allows a symlink here, you can’t create the configuration in place.

## Behaviour

The `configfs` virtual file system does **not** behave like a regular disk file system in many ways. Some examples:

- You cannot create arbitrary files or folders, or rename them, but you can only create items at predefined places with predefined names.
- When writing parameters into files, it might require the values to be in a certain format (i.e., the parameters are essentially validated at write-time).
- Changes are effectuated immediately and synchronously, just as if you had made calls to the respective system API directly, e.g. via C functions. Unlike with other file-based configurations, you don’t have to restart any service or such.
- Sometimes, operations must be carried out in a specific order that depends on internal logic rather than on conventional file system rules. E.g., when writing parameters into existing files, it might only work if that’s done in a specific order.
- When creating a new `functions/` sub-folder, the kernel automatically and immediately sets up a content structure of files and sub-folders. As mentioned above, that structure is fixed and can’t be changed.
- Folders can only be deleted via `rmdir`, not via `rm -rf`. That’s even true if the folder isn’t empty, in which case `rmdir` would usually fail.
- `functions/` folders can only be deleted when they are **not** referenced by a symlink from the `configs/c.1/` folder, otherwise the deletion attempt fails.
- Symlinks have special meaning, and creating or deleting them might have side-effects. Also, `configfs` items cannot be symlinked from outside the virtual file system.
- Some operations can only be carried out while the gadget is deactivated, or they only take effect after re-activating the gadget.
- Configuration changes that are made while the gadget is active might silently fail, i.e. they could leave the entire gadget in an inconsistent or broken state, despite the command itself returning exit code `0`. Therefore, it’s important to be mindful of potential failure cases.
