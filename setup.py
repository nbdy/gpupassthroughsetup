#!/bin/python3


class Configuration(object):
    CPU_INTEL = 0
    CPU_AMD = 1

    GPU_NVIDIA = 0
    GPU_ATI = 1

    GPU = {
        GPU_NVIDIA: "nvidia",
        GPU_ATI: "amd"
    }

    cpu = None
    gpu = None
    pci_ids = ""

    @staticmethod
    def help():
        print("usage: python3 setup.py {arguments}")
        print("{arguments}:")
        print("\t-c\t--cpu\t\tamd|intel")
        print("\t-g\t--gpu\t\tnvidia|amd")
        print("\t-p\t--pci-id\tshould get detected automatically")
        exit()

    @staticmethod
    def parse_arguments(arguments):
        c = Configuration()
        i = 0
        while i < len(arguments):
            a = arguments[i]
            if a in ["-c", "--cpu"]:
                if arguments[i + 1] in ["intel"]:
                    c.cpu = Configuration.CPU_INTEL
                elif arguments[i + 1] in ["amd"]:
                    c.cpu = Configuration.CPU_AMD
            elif a in ["-g", "--gpu"]:
                if arguments[i + 1] in ["amd", "ati"]:
                    c.gpu = Configuration.GPU_ATI
                elif arguments[i + 1] in ["nvidia"]:
                    c.gpu = Configuration.GPU_NVIDIA
            elif a in ["-p", "--pci-id"]:
                c.pci_ids += arguments[i + 1]
                c.pci_ids += ","
            elif a in ["-h", "--help"]:
                Configuration.help()
            i += 1
        c.pci_ids = c.pci_ids[0:-1]
        return c


def generate_grub_default(pci_ids, splash=False, intel=True, infile="grub_default.txt"):
    c = open(infile).read()
    if splash:
        c = c.replace("{{splash}}", "splash")
    else:
        c = c.replace("{{splash}}", "nosplash")
    if intel:
        c = c.replace("{{iommu}}", "intel_iommu=on")
    else:
        c = c.replace("{{iommu}}", "amd_iommu=on iommu=pt")
    c = c.replace("{{pci_ids}}", pci_ids)
    with open("/etc/default/grub", "w") as o:
        o.write(c)


def get_pci_ids(gpu=Configuration.GPU_ATI):
    gpu = Configuration.GPU[gpu]
    from subprocess import Popen, PIPE
    p = Popen(["lspci", "-knn"], stdout=PIPE)
    ids = ""
    vga_found = False
    for line in p.stdout.readlines():
        line = str(line[0:-1].lower())
        if not line.startswith('\t'):
            if (gpu in line and "vga" in line) or ((gpu in line and "audio" in line) and vga_found):
                vga_found = True
                vals = line.split(" ")
                for v in vals:
                    if v.endswith("'"):
                        v = v[0:-1]
                    if len(v) == 11 and v.startswith("["):
                        ids += v[1:-1]
                        ids += ","
    ids = ids[0:-1]
    return ids


def install_virt_setup_modprobe(pci_ids):
    i = open("virt_setup.conf").read()
    i = i.replace("{{pci_ids}}", pci_ids)
    with open("/etc/modprobe.d/virt-setup.conf", "w") as o:
        o.write(i)


def install_initramfs_modules(pci_ids):
    i = open("initramfs_modules").read()
    i = i.replace("{{pci_ids}}", pci_ids)
    with open("/etc/initramfs-tools/modules", "w") as o:
        o.write(i)


def install_modules(pci_ids):
    i = open("modules").read()
    i = i.replace("{{pci_ids}}", pci_ids)
    with open("/etc/modules", "w") as o:
        o.write(i)


def banner():
    print("!!!!!!! ATTENTION !!!!!!!")
    print("this script will overwrite following files:")
    print("/etc/modprobe.d/virt-setup.conf")
    print("/etc/initramfs-tools/modules")
    print("/etc/modules")
    print("/etc/default/grub")
    print("this tool will NOT back those files up")


def main():
    from os import system, geteuid
    from sys import argv
    c = Configuration.parse_arguments(argv)
    if c.gpu is None:
        print("what am is supposed to pass through?")
        exit()
    if c.gpu == Configuration.GPU_NVIDIA:
        print("i did not test this, there should be no support for it")
    if geteuid() != 0:
        print("please run with sudo or as root")
        exit()
    banner()
    yn = raw_input("[CONTINUE] > ")
    if yn != "CONTINUE":
        print("user didn't enter 'CONTINUE'")
        exit()
    if c.pci_ids == "":
        c.pci_ids = get_pci_ids(c.gpu)
    generate_grub_default(c.pci_ids)
    system("update-grub")
    install_virt_setup_modprobe(c.pci_ids)
    install_initramfs_modules(c.pci_ids)
    install_modules(c.pci_ids)
    system("update-initramfs -u")
    print("all done")
    print("you should reboot now")
    print("if you have not done yet, add your pci devices to your kvm machine")


if __name__ == '__main__':
    main()
