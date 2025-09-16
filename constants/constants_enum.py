from enum import Enum


class StageStatus(Enum):
    Wait = 0
    Execute = 1
    Stop = 2
    Error = 3

class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    AAC = "aac"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"

class FaceBlendShape(Enum):
    EyeBlinkLeft = 0
    EyeLookDownLeft = 1
    EyeLookInLeft = 2
    EyeLookOutLeft = 3
    EyeLookUpLeft = 4
    EyeSquintLeft = 5
    EyeWideLeft = 6
    EyeBlinkRight = 7
    EyeLookDownRight = 8
    EyeLookInRight = 9
    EyeLookOutRight = 10
    EyeLookUpRight = 11
    EyeSquintRight = 12
    EyeWideRight = 13
    JawForward = 14
    JawLeft = 15
    JawRight = 16
    JawOpen = 17
    MouthClose = 18
    MouthFunnel = 19
    MouthPucker = 20
    MouthLeft = 21
    MouthRight = 22
    MouthSmileLeft = 23
    MouthSmileRight = 24
    MouthFrownLeft = 25
    MouthFrownRight = 26
    MouthDimpleLeft = 27
    MouthDimpleRight = 28
    MouthStretchLeft = 29
    MouthStretchRight = 30
    MouthRollLower = 31
    MouthRollUpper = 32
    MouthShrugLower = 33
    MouthShrugUpper = 34
    MouthPressLeft = 35
    MouthPressRight = 36
    MouthLowerDownLeft = 37
    MouthLowerDownRight = 38
    MouthUpperUpLeft = 39
    MouthUpperUpRight = 40
    BrowDownLeft = 41
    BrowDownRight = 42
    BrowInnerUp = 43
    BrowOuterUpLeft = 44
    BrowOuterUpRight = 45
    CheekPuff = 46
    CheekSquintLeft = 47
    CheekSquintRight = 48
    NoseSneerLeft = 49
    NoseSneerRight = 50
    TongueOut = 51
    HeadRoll = 52
    HeadPitch = 53
    HeadYaw = 54
    TongueTipUp = 55
    TongueTipDown = 56
    TongueTipLeft = 57
    TongueTipRight = 58
    TongueRollUp = 59
    TongueRollDown = 60
    TongueRollLeft = 61
    TongueRollRight = 62
    TongueUp = 63
    TongueDown = 64
    TongueLeft = 65
    TongueRight = 66
    TongueIn = 67
    TongueStretch = 68
    TongueWide = 69
    TongueNarrow = 70

class EmotionType(Enum):
    AMAZINGMENT = "amazement"
    ANGER = "anger"
    CHEEKYNESS = "cheekiness"
    DISGUST = "disgust"
    FEAR = "fear"
    GRIEF = "grief"
    JOY = "joy"
    OUTOFBREATH = "outofbreath"
    PAIN = "pain"
    SADNESS = "sadness"
    NEUTRAL = "neutral"

class BodyPart(Enum):
    UpperBody = 0
    LowerBody = 1
    Head = 2
    LeftArm = 3
    RightArm = 4
    LeftLeg = 5
    RightLeg = 6


class SkeletonJoint(Enum):
    Pelvis = 0
    LeftHip = 1
    RightHip = 2
    Spine1 = 3
    LeftKnee = 4
    RightKnee = 5
    Spine2 = 6
    LeftAnkle = 7
    RightAnkle = 8
    Spine3 = 9
    LeftFoot = 10
    RightFoot = 11
    Neck = 12
    LeftCollar = 13
    RightCollar = 14
    Head = 15
    LeftShoulder = 16
    RightShoulder = 17
    LeftElbow = 18
    RightElbow = 19
    LeftWrist = 20
    RightWrist = 21
    Jaw = 22
    LeftEyeSmplhf = 23
    RightEyeSmplhf = 24
    LeftIndex1 = 25
    LeftIndex2 = 26
    LeftIndex3 = 27
    LeftMiddle1 = 28
    LeftMiddle2 = 29
    LeftMiddle3 = 30
    LeftPinky1 = 31
    LeftPinky2 = 32
    LeftPinky3 = 33
    LeftRing1 = 34
    LeftRing2 = 35
    LeftRing3 = 36
    LeftThumb1 = 37
    LeftThumb2 = 38
    LeftThumb3 = 39
    RightIndex1 = 40
    RightIndex2 = 41
    RightIndex3 = 42
    RightMiddle1 = 43
    RightMiddle2 = 44
    RightMiddle3 = 45
    RightPinky1 = 46
    RightPinky2 = 47
    RightPinky3 = 48
    RightRing1 = 49
    RightRing2 = 50
    RightRing3 = 51
    RightThumb1 = 52
    RightThumb2 = 53
    RightThumb3 = 54

class StageExceptionType(Enum):
    # Resource Errors (1xx)
    RESOURCE_NOT_FOUND = 100
    RESOURCE_UNAVAILABLE = 101
    RESOURCE_EXHAUSTED = 102
    RESOURCE_TIMEOUT = 103
    
    # Data Validation Errors (2xx)
    INVALID_DATA_FORMAT = 200
    INVALID_DATA_SIZE = 201
    INVALID_DATA_CONTENT = 202
    INVALID_DATA_SEQUENCE = 203
    MISSING_REQUIRED_DATA = 204
    
    # Runtime Errors (3xx)
    EXECUTION_FAILED = 300
    PROCESSING_TIMEOUT = 301
    INTERNAL_ERROR = 302
    DEPENDENCY_FAILED = 303
    
    # Stage Errors (4xx)
    INVALID_STATE_TRANSITION = 400
    STAGE_NOT_INITIALIZED = 401
    STAGE_ALREADY_RUNNING = 402
    STAGE_NOT_RUNNING = 403
    STAGE_EXECUTE_FAILED = 404
    
    # System Errors (5xx)
    SYSTEM_OVERLOAD = 500
    MEMORY_ERROR = 501
    DISK_ERROR = 502
    NETWORK_ERROR = 503
    
    # Configuration Errors (6xx)
    CONFIG_NOT_FOUND = 600
    INVALID_CONFIG = 601
    CONFIG_CONFLICT = 602
    
    # External Service Errors (7xx)
    SERVICE_UNAVAILABLE = 700
    SERVICE_TIMEOUT = 701
    SERVICE_ERROR = 702
    
    # Recovery Errors (8xx)
    RECOVERY_FAILED = 800
    RETRY_EXHAUSTED = 801
    UNRECOVERABLE_ERROR = 802

