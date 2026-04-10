import math

Incl_Xgain = 1.07
Incl_Xoffset = 132
Incl_Ygain = 1.15
Incl_Yoffset = 131


def getIncValue(bytes):

    byte11 = int(bytes[0])
    byte12 = int(bytes[1])

    X = (byte11 - Incl_Xoffset) * Incl_Xgain
    Y = (byte12 - Incl_Yoffset) * Incl_Ygain

    X_rad = math.radians(X)
    Y_rad = math.radians(Y)

    inclination = math.atan(
        math.sqrt(
            math.tan(X_rad)**2 + math.tan(Y_rad)**2
        )
    )

    inclination_deg = math.degrees(inclination)

    return X,Y

print(getIncValue([134,154]))