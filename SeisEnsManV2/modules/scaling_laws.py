import sys
import math
from numpy import power, log10

def scalinglaw_Tonini_WC(**kwargs):

    mag        = kwargs.get('mag', None)
    cfg        = kwargs.get('cfg', None)
    type_scala = kwargs.get('type_scala', None)

    if (type_scala == 'M2L'):
        a =-2.440
        b =0.590
        y = 10.**(a+b*mag)

    elif (type_scala == 'M2W'):
        a=-1.010
        b=0.320
        y = 10.**(a+b*mag)

    else:
        print("Scaling law in scalinglaw_Tonini_WC not recognized. Exit!")
        sys.exit()

    return y

def scalinglaw_Tonini_Murotani(**kwargs):

    mag        = kwargs.get('mag', None)
    cfg        = kwargs.get('cfg', None)
    type_scala = kwargs.get('type_scala', None)

    a    = -3.806
    b    = 1.000
    Area = 10**(a+b*mag)

    if (type_scala == 'M2L'):
        y = math.sqrt(2.5*Area)/2.5

    elif (type_scala == 'M2W'):
        y = math.sqrt(2.5*Area)

    else:
        print("Scaling law in scalinglaw_Tonini_Murotani not recognized. Exit!")
        sys.exit()

    return y

def mag_to_w_leonardo(**kwargs):

    mag = kwargs.get('mag', None)
    rake = kwargs.get('rake', None)
    
    # Coefficients from Leonardo 2014

    if rake>-135 and rake<=-45: #normal
        a=-1.31
        b=0.31
    elif rake>45 and rake<=135: #reverse
        a=-1.29
        b=0.3
    else: #strike-slip
        a=-1.1
        b=0.28

    w = 1000.0 * 10.**(a+b*mag)

    return w

def mag_to_a_leonardo(**kwargs):

    mag = kwargs.get('mag', None)
    rake = kwargs.get('rake', None)

    # Coefficients from Leonardo 2014

    if rake is None:
        # Return average of strike-slip and dip-slip curves
        return power(10.0, (mag - 3.995))
    elif (-45 <= rake <= 45) or (rake >= 135) or (rake <= -135):
        # strike slip
        return power(10.0, (mag - 3.99))
    else:
        # Dip slip (thrust or normal), and undefined rake
        return power(10.0, (mag - 4.00))

def mag_to_w_BS_leonardo(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 1000.0 * scalinglaw_Tonini_Murotani(mag=mag, type_scala='M2W')

    return out

def mag_to_l_BS(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 1000.0 * scalinglaw_Tonini_WC(mag=mag, type_scala='M2L')

    return out

def mag_to_l_PS(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 1000.0 * scalinglaw_Tonini_Murotani(mag=mag, type_scala='M2W')

    return out

def mag_to_w_PS(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 1000.0 * scalinglaw_Tonini_Murotani(mag=mag, type_scala='M2W')

    return out


def mag_to_l_PS_mo(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 1000.0 * scalinglaw_Tonini_Murotani(mag=mag, type_scala='M2W')

    return out

def mag_to_l_PS_st(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 1000.0 * scalinglaw_Tonini_Murotani(mag=mag, type_scala='M2W')

    return out


def mag_to_w_BS(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 1000.0 * scalinglaw_Tonini_WC(mag=mag, type_scala='M2W')

    return out

def mag_to_w_PS_mo(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 1000.0 * scalinglaw_Tonini_Murotani(mag=mag, type_scala='M2W')

    return out

def mag_to_w_PS_st(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 1000.0 * scalinglaw_Tonini_Murotani(mag=mag, type_scala='M2W')

    return out

def correct_BS_horizontal_position(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = 0.5 * mag_to_l_BS(mag=mag)

    return out

def correct_BS_vertical_position(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = math.sin(math.pi/4)*0.5 * mag_to_w_BS(mag=mag)

    return out

def correct_PS_horizontal_position(**kwargs):

    mag       = kwargs.get('mag', None)
    Config    = kwargs.get('cfg', None)

    out = 0.5 * mag_to_l_PS(mag=mag)

    return out

def correct_PS_vertical_position(**kwargs):

    mag = kwargs.get('mag', None)
    cfg = kwargs.get('cfg', None)

    out = math.sin(math.pi/4)*0.5 * mag_to_w_PS(mag=mag)

    return out
