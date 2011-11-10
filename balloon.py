import os
import time
import android

phoneNumber="15555555555"
period = 1 # seconds
gpsperiod = 5
magperiod = 1
oriperiod = 1
accperiod = 1
picperiod = 30
smsperiod = 30

# FOR TESTING
maxtick = 90 # FOR TESTING
gpsflag = False
magflag = True
oriflag = True
accflag = True
smsflag = False
picflag = False
logmode = 'w' # FOR TESTING (for reply use 'a')
bufsize = 0

droid = android.Android()
droid.startSensing()
droid.wakeLockAcquireDim()
droid.startLocating(gpsperiod * 1000, 1) # period ms, dist

maglog = open('/sdcard/balloon/mag.log', logmode, bufsize)
orilog = open('/sdcard/balloon/ori.log', logmode, bufsize)
acclog = open('/sdcard/balloon/acc.log', logmode, bufsize)
picdir = '/sdcard/balloon/pics/'
pictemp = picdir + '%05i.jpg'
gpslog = open('/sdcard/balloon/gps.log', logmode, bufsize)
smslog = open('/sdcard/balloon/sms.log', logmode, bufsize)
lastloc = ""

tick = 0
piccount = len(os.listdir(picdir))
while (tick < maxtick):
    if ((tick % magperiod) == 0) and magflag:
        magr = droid.sensorsReadMagnetometer()
        mag = magr.result
        print "MAG:", mag
        if (not (mag is None)) and (type(mag) is list) and (len(mag) == 3) and (not (mag[0] is None)):
            maglog.write("%.5f, %.5f, %.5f, %.5f\n" % (time.time(), mag[0], mag[1], mag[2]))
    if ((tick % oriperiod) == 0) and oriflag:
        orir = droid.sensorsReadOrientation()
        ori = orir.result
        print "ORI:", ori
        if (not (ori is None)) and (type(ori) is list) and (len(ori) == 3) and (not (ori[0] is None)):
            orilog.write("%.5f, %.5f, %.5f, %.5f\n" % (time.time(), ori[0], ori[1], ori[2]))
    if ((tick % accperiod) == 0) and accflag:
        accr = droid.sensorsReadAccelerometer()
        acc = accr.result
        print "ACC:", acc
        if (not (acc is None)) and (type(acc) is list) and (len(acc) == 3) and (not (acc[0] is None)):
            acclog.write("%.5f, %.5f, %.5f, %.5f\n" % (time.time(), acc[0], acc[1], acc[2]))
    if ((tick % picperiod) == 0) and picflag:
        droid.cameraCapturePicture(pictemp % piccount, True)
        piccount += 1
    if ((tick % gpsperiod) == 0) and gpsflag:
        r = droid.readLocation()
        loc = r.result
        print "LOC:", loc
        if 'gps' in loc:
            if not (loc['gps'] is None):
                packet = loc['gps']
                al = packet.get('altitude',0.0)
                lo = packet.get('longitude',0.0)
                ti = packet.get('time',0)
                la = packet.get('latitude',0.0)
                sp = packet.get('speed',0)
                ac = packet.get('accuracy',0)
                lastloc = "1, %i, %.5f, %.5f, %.5f, %.5f, %i" % (ti, lo, la, al, sp, ac)
                gpslog.write(lastloc + "\n")
        elif 'network' in loc:
            if not (loc['network'] is None):
                packet = loc['network']
                al = packet.get('altitude',0.0)
                lo = packet.get('longitude',0.0)
                ti = packet.get('time',0)
                la = packet.get('latitude',0.0)
                sp = packet.get('speed',0)
                ac = packet.get('accuracy',0)
                lastloc = "0, %i, %.5f, %.5f, %.5f, %.5f, %i" % (ti, lo, la, al, sp, ac)
                gpslog.write(lastloc + "\n")
    if ((tick % smsperiod) == 0) and smsflag:
        print "SMS:", lastloc
        if lastloc != "":
            try:
                droid.smsSend(phoneNumber, lastloc)
                smslog.write("sms passed: %s\n" % lastloc)
            except:
                smslog.write("sms failed: %s\n" % lastloc)
    time.sleep(period)
    tick += 1
