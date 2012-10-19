# Copyright (C) 2011 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

$(call inherit-product, $(SRC_TARGET_DIR)/product/languages_full.mk)

# The gps config appropriate for this device
$(call inherit-product, device/common/gps/gps_us_supl.mk)

$(call inherit-product-if-exists, vendor/asus/tf700t/tf700t-vendor.mk)

DEVICE_PACKAGE_OVERLAYS += device/asus/tf700t/overlay


# This device is hdpi.
PRODUCT_AAPT_CONFIG := xlarge hdpi mdpi
PRODUCT_AAPT_PREF_CONFIG := hdpi
#PRODUCT_LOCALES += hdpi

# Prebuilt kernel location
ifeq ($(TARGET_PREBUILT_KERNEL),)
        LOCAL_KERNEL := device/asus/tf700t/prebuilt/kernel
else
        LOCAL_KERNEL := $(TARGET_PREBUILT_KERNEL)
endif

# Files needed for boot image
PRODUCT_COPY_FILES += \
    $(LOCAL_KERNEL):kernel \
    $(LOCAL_PATH)/ramdisk/init.cardhu.rc:root/init.cardhu.rc \
    $(LOCAL_PATH)/ramdisk/init.cardhu.keyboard.rc:root/init.cardhu.keyboard.rc \
    $(LOCAL_PATH)/ramdisk/ueventd.cardhu.rc:root/ueventd.cardhu.rc \
    $(LOCAL_PATH)/ramdisk/init.cardhu.usb.rc:root/init.cardhu.usb.rc \
    $(LOCAL_PATH)/ramdisk/init.cardhu.cpu.rc:root/init.cardhu.cpu.rc \
    $(LOCAL_PATH)/ramdisk/fstab.cardhu:root/fstab.cardhu

# Kernel modules
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/prebuilt/lib/baseband_usb_chr.ko:system/lib/modules/baseband_usb_chr.ko \
    $(LOCAL_PATH)/prebuilt/lib/raw_ip_net.ko:system/lib/modules/raw_ip_net.ko 

# Prebuilt configuration files
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/prebuilt/cpu.sh:system/bin/cpu.sh \
    $(LOCAL_PATH)/prebuilt/vold.fstab:system/etc/vold.fstab \
    $(LOCAL_PATH)/prebuilt/gpsconfig.xml:system/etc/gps/gpsconfig.xml \
    $(LOCAL_PATH)/prebuilt/mixer_paths.xml:system/etc/mixer_paths.xml 

# Input device configuration files
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/idc/atmel-maxtouch.idc:system/usr/idc/atmel-maxtouch.idc \
    $(LOCAL_PATH)/idc/elantech_touchscreen.idc:system/usr/idc/elantech_touchscreen.idc \
    $(LOCAL_PATH)/idc/elan-touchscreen.idc:system/usr/idc/elan-touchscreen.idc \
    $(LOCAL_PATH)/idc/panjit_touch.idc:system/usr/idc/panjit_touch.idc \
    $(LOCAL_PATH)/idc/qwerty2.idc:system/usr/idc/qwerty2.idc \
    $(LOCAL_PATH)/idc/qwerty.idc:system/usr/idc/qwerty.idc \
    $(LOCAL_PATH)/idc/raydium_ts.idc:system/usr/idc/raydium_ts.idc \
    $(LOCAL_PATH)/idc/sis_touch.idc:system/usr/idc/sis_touch.idc \
    $(LOCAL_PATH)/idc/Vendor_0457_Product_0817.idc:system/usr/idc/Vendor_0457_Product_0817.idc \
    $(LOCAL_PATH)/prebuilt/asusdec.kcm:system/usr/keychars/asusdec.kcm \
    $(LOCAL_PATH)/prebuilt/asusdec.kl:system/usr/keylayout/asusdec.kl \
    $(LOCAL_PATH)/prebuilt/gpio-keys.kl:system/usr/keylayout/gpio-keys.kl \
    $(LOCAL_PATH)/prebuilt/tegra-kbc.kl:system/usr/keylayout/tegra-kbc.kl

# These are the hardware-specific features
PRODUCT_COPY_FILES += \
    frameworks/native/data/etc/tablet_core_hardware.xml:system/etc/permissions/tablet_core_hardware.xml \
    frameworks/native/data/etc/android.hardware.camera.flash-autofocus.xml:system/etc/permissions/android.hardware.camera.flash-autofocus.xml \
    frameworks/native/data/etc/android.hardware.camera.xml:system/etc/permissions/android.hardware.camera.xml \
    frameworks/native/data/etc/android.hardware.camera.front.xml:system/etc/permissions/android.hardware.camera.front.xml \
    frameworks/native/data/etc/android.hardware.location.xml:system/etc/permissions/android.hardware.location.xml \
    frameworks/native/data/etc/android.hardware.location.gps.xml:system/etc/permissions/android.hardware.location.gps.xml \
    frameworks/native/data/etc/android.hardware.wifi.xml:system/etc/permissions/android.hardware.wifi.xml \
    frameworks/native/data/etc/android.hardware.wifi.direct.xml:system/etc/permissions/android.hardware.wifi.direct.xml \
    frameworks/native/data/etc/android.hardware.sensor.compass.xml:system/etc/permissions/android.hardware.sensor.compass.xml \
    frameworks/native/data/etc/android.hardware.sensor.light.xml:system/etc/permissions/android.hardware.sensor.light.xml \
    frameworks/native/data/etc/android.hardware.sensor.gyroscope.xml:system/etc/permissions/android.hardware.sensor.gyroscope.xml \
    frameworks/native/data/etc/android.hardware.sensor.accelerometer.xml:system/etc/permissions/android.hardware.sensor.accelerometer.xml \
    frameworks/native/data/etc/android.hardware.touchscreen.multitouch.jazzhand.xml:system/etc/permissions/android.hardware.touchscreen.multitouch.jazzhand.xml \
    frameworks/native/data/etc/android.software.sip.voip.xml:system/etc/permissions/android.software.sip.voip.xml \
    frameworks/native/data/etc/android.hardware.usb.accessory.xml:system/etc/permissions/android.hardware.usb.accessory.xml \
    frameworks/native/data/etc/android.hardware.usb.host.xml:system/etc/permissions/android.hardware.usb.host.xml \
    packages/wallpapers/LivePicker/android.software.live_wallpaper.xml:system/etc/permissions/android.software.live_wallpaper.xml \
    $(LOCAL_PATH)/asusdec/com.cyanogenmod.asusdec.xml:system/etc/permissions/com.cyanogenmod.asusdec.xml


# Build characteristics setting
PRODUCT_CHARACTERISTICS := tablet

# This device have enough room for precise davick
PRODUCT_TAGS += dalvik.gc.type-precise

# torch app
#PRODUCT_PACKAGES += \
#	Torch

# Extra packages to build for this device
PRODUCT_PACKAGES += \
    librs_jni \
    com.android.future.usb.accessory \
    make_ext4fs \
    setup_fs \
    audio.primary.cardhu \
    audio.a2dp.default \
    audio.usb.default \
    libtinyalsa \
    libaudioutils \
    tinymix \
    tinyplay \
    tinyrec \
    libinvensense_mpl \
    AutoParts_tfp \
    blobpack_tfp \
    mischelp \
    com.cyanogenmod.asusdec \
    libasusdec_jni \
    Camera \
    camera.tegra

# Propertys spacific for this device
PRODUCT_PROPERTY_OVERRIDES := \
    wifi.interface=wlan0 \
    wifi.supplicant_scan_interval=15 \
    ro.opengles.version=131072 \
    persist.sys.usb.config=mtp,adb

# Tegra 3 spacific overrides
PRODUCT_PROPERTY_OVERRIDES += \
    persist.tegra.nvmmlite=1 \
    persist.sys.NV_FPSLIMIT=60

# UI
PRODUCT_PROPERTY_OVERRIDES += \
    debug.performance.tuning=1 \
    video.accelerate.hw=1 \
    ro.kernel.android.checkjni=0 \
    ro.kernel.checkjni=0 \
    ro.mot.eri.losalert.delay=1000 \
    persist.sys.strictmode.visual=0 \
    persist.sys.strictmode.disable=1 \
    dalvik.vm.execution-mode=int:jit \
    com.ti.omap_enhancement=true \
   windowsmgr.max_events_per_sec=300

# Prime specific overrides
PRODUCT_PROPERTY_OVERRIDES += \
    ro.epad.model=TF700T \
    ro.product.model=TF700T

# media files
PRODUCT_COPY_FILES += \
    device/asus/tf700t/media_codecs.xml:system/etc/media_codecs.xml \
    device/asus/tf700t/media_profiles.xml:system/etc/media_profiles.xml

# Inherit tablet dalvik settings
$(call inherit-product, frameworks/native/build/tablet-dalvik-heap.mk)

# Call the vendor to setup propiatory files
$(call inherit-product-if-exists, vendor/asus/tf700t/tf700t-vendor.mk)

# Copy bcm4330 firmware
# $(call inherit-product-if-exists, hardware/broadcom/wlan/bcmdhd/firmware/bcm4330/device-bcm.mk)

# Device naming
PRODUCT_BUILD_PROP_OVERRIDES += BUILD_UTC_DATE=0
PRODUCT_NAME := full_tf700t
PRODUCT_DEVICE := tf700t
PRODUCT_MODEL := tf700t
PRODUCT_BRAND := asus
PRODUCT_MANUFACTURER := asus
