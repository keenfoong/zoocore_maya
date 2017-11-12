from maya.api import OpenMaya as om2
kMFnNumericBoolean = 0
kMFnNumericShort = 1
kMFnNumericInt = 2
kMFnNumericLong = 3
kMFnNumericByte = 3
kMFnNumericFloat = 4
kMFnNumericDouble = 5
kMFnNumericAddr = 6
kMFnNumericChar = 8
kMFnUnitAttributeDistance = 9
kMFnUnitAttributeAngle = 10
kMFnUnitAttributeTime = 11
kMFnkEnumAttribute = 12
kMFnDataString = 13
kMFnDataMatrix = 14
kMFnDataFloatArray = 15
kMFnDataDoubleArray = 16
kMFnDataIntArray = 17
kMFnDataPointArray = 18
kMFnDataVectorArray = 19
kMFnDataStringArray = 20
kMFnDataMatrixArray = 21
kMFnCompoundAttribute = 22
kMFnNumericInt64 = 23
kMFnNumericLast = 24
kMFnNumeric2Double = 25
kMFnNumeric2Float = 26
kMFnNumeric2Int = 27
kMFnNumeric2Long = 28
kMFnNumeric2Short = 29
kMFnNumeric3Double = 30
kMFnNumeric3Float = 31
kMFnNumeric3Int = 32
kMFnNumeric3Long = 33
kMFnNumeric3Short = 34
kMFnNumeric4Double = 35
kMFnMessageAttribute = 36


def mayaTypeFromType(Type):
    if Type == kMFnNumericBoolean:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kBoolean
    elif Type == kMFnNumericByte:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kByte
    elif Type == kMFnNumericShort:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kShort
    elif Type == kMFnNumericInt:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kInt
    elif Type == kMFnNumericLong:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kLong
    elif Type == kMFnNumericDouble:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kDouble
    elif Type == kMFnNumericFloat:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kFloat
    elif Type == kMFnNumericAddr:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kAddr
    elif Type == kMFnNumericChar:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kChar
    elif Type == kMFnNumeric2Double:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Double
    elif Type == kMFnNumeric2Float:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Float
    elif Type == kMFnNumeric2Int:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Int
    elif Type == kMFnNumeric2Long:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Long
    elif Type == kMFnNumeric2Short:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Short
    elif Type == kMFnNumeric3Double:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Double
    elif Type == kMFnNumeric3Float:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Float
    elif Type == kMFnNumeric3Int:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Int
    elif Type == kMFnNumeric3Long:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Long
    elif Type == kMFnNumeric3Short:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Short
    elif Type == kMFnNumeric4Double:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k4Double

    if Type == kMFnUnitAttributeDistance:
        return om2.MFnUnitAttribute, om2.MFnUnitAttribute.kDistance
    elif Type == kMFnUnitAttributeAngle:
        return om2.MFnUnitAttribute, om2.MFnUnitAttribute.kAngle
    elif Type == kMFnUnitAttributeTime:
        return om2.MFnUnitAttribute, om2.MFnUnitAttribute.kTime
    elif Type == kMFnkEnumAttribute:
        return om2.MFnEnumAttribute, om2.MFn.kEnumAttribute

    if Type == kMFnDataString:
        return om2.MFnTypedAttribute, om2.MFnData.kString
    elif Type == kMFnDataMatrix:
        return om2.MFnTypedAttribute,om2.MFnData.kMatrix
    elif Type == kMFnDataFloatArray:
        return om2.MFnTypedAttribute,om2.MFnData.kFloatArray
    elif Type == kMFnDataDoubleArray:
        return om2.MFnTypedAttribute,om2.MFnData.kDoubleArray
    elif Type == kMFnDataIntArray:
        return om2.MFnTypedAttribute,om2.MFnData.kIntArray
    elif Type == kMFnDataPointArray:
        return om2.MFnTypedAttribute,om2.MFnData.kPointArray
    elif Type == kMFnDataVectorArray:
        return om2.MFnTypedAttribute,om2.MFnData.kVectorArray
    elif Type == kMFnDataStringArray:
        return om2.MFnTypedAttribute,om2.MFnData.kStringArray
    elif Type == kMFnDataMatrixArray:
        return om2.MFnTypedAttribute,om2.MFnData.kMatrixArray

    elif Type == kMFnMessageAttribute:
        return om2.MFnMessageAttribute, om2.MFn.kMessageAttribute
    return None, None
