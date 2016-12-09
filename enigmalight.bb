DESCRIPTION = "An Ambilight clone for broadcom based linux receivers."
HOMEPAGE = "https://github.com/Speedy1985/enigmalight"
LICENSE = "GPLv3"
LIC_FILES_CHKSUM = "file://README;md5=93285fcad54271879db50c1fbf22d98b"

DEPENDS = "libusb1"

inherit gitpkgv autotools

SRCREV = "${AUTOREV}"
PV = "1.0+git${SRCPV}"
PKGV = "1.0+git${GITPKGV}"

#SRC_URI = "git://github.com/Speedy1985/enigmalight.git"
SRC_URI = "git://github.com/Dima73/enigmalight.git"

S = "${WORKDIR}/git/build"

do_configure() {
    cd ${S}
    oe_runconf
}

do_compile() {
    cd ${S}
    oe_runmake
}

do_install() {
    cd ${S}
    oe_runmake DESTDIR=${D} install
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions
    cp -R ${S}/python/plugin/EnigmaLight ${D}${libdir}/enigma2/python/Plugins/Extensions
}

FILES_${PN} += "${libdir}/enigma2/python/Plugins/Extensions/EnigmaLight/"
