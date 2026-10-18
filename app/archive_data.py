"""Allowlisted local archives. Never retain access codes or other players' identities."""
import math
from app.score_times import latest_time

NOTE_TYPES=('tap','hold','slide','touch','break')
JUDGEMENTS=('CriticalPerfect','Perfect','Great','Good','Miss')
ITEM_KINDS={1:('plate','姓名框'),2:('title','称号'),3:('icon','头像'),5:('music','歌曲解锁'),
    6:('music','MASTER解锁'),7:('music','Re:MASTER解锁'),8:('music','强制解锁'),
    9:('chara','角色'),10:('partner','搭档'),11:('frame','背景框'),12:('ticket','票券')}
PROFILE_FIELDS='userName isNetMember nameplateId iconId trophyId plateId titleId partnerId frameId selectMapId totalAwake gradeRating musicRating playerRating highestRating gradeRank classRank courseRank charaSlot charaLockSlot contentBit playCount eventWatchedDate lastGameId lastRomVersion lastDataVersion lastLoginDate lastPlayDate lastPlayCredit lastPlayMode lastPlaceId lastPlaceName lastRegionId lastRegionName lastCountryCode lastSelectEMoney lastSelectTicket lastSelectCourse lastCountCourse firstGameId firstRomVersion firstDataVersion firstPlayDate compatibleCmVersion dailyBonusDate dailyCourseBonusDate lastPairLoginDate lastTrialPlayDate playVsCount playSyncCount winCount helpCount comboCount totalDeluxscore totalBasicDeluxscore totalAdvancedDeluxscore totalExpertDeluxscore totalMasterDeluxscore totalReMasterDeluxscore totalHiscore totalBasicHighscore totalAdvancedHighscore totalExpertHighscore totalMasterHighscore totalReMasterHighscore totalSync totalBasicSync totalAdvancedSync totalExpertSync totalMasterSync totalReMasterSync totalAchievement totalBasicAchievement totalAdvancedAchievement totalExpertAchievement totalMasterAchievement totalReMasterAchievement playerOldRating playerNewRating dateTime cmLastEmoneyBrand cmLastEmoneyCredit mapStock point totalPoint currentPlayCount renameCredit'.split()
OPTION_FIELDS='adjustTiming ansVolume breakSe breakSlideVolume breakVolume brightness criticalSe damageSeVolume dispBar dispCenter dispChain dispJudge dispJudgePos dispJudgeTouchPos dispRate exSe exVolume headPhoneVolume holdDesign judgeTiming matching mirrorMode noteSize noteSpeed optionKind outFrameType outlineDesign slideDesign slideSe slideSize slideSpeed slideVolume sortMusic sortTab starRotate starType submonitorAchive submonitorAnimation submonitorAppeal tapDesign tapHoldVolume tapSe touchEffect touchHoldVolume touchSize touchSpeed touchVolume trackSkip'.split()
EXTEND_FIELDS='categoryIndex encountMapNpcList extendContentBit extraFlag isGotoCodeRead isPhotoAgree musicIndex playStatusSetting selectDifficultyId selectMusicId selectResultDetails selectResultScoreViewType selectScoreType selectedCardList sortCategorySetting sortMusicSetting'.split()
UDEMAE_FIELDS='classValue loseNum maxClassValue maxLoseNum maxRate maxWinNum npcLoseNum npcMaxLoseNum npcMaxWinNum npcTotalLoseNum npcTotalWinNum npcWinNum rate totalLoseNum totalWinNum winNum'.split()
LOG_FIELDS=('achievement afterDeluxRating afterGrade afterGradeRank afterRating beforeDeluxRating beforeGrade beforeRating comboStatus deluxscore fastCount lateCount isAchieveNewRecord isAllPerfect isBreak isClear isCriticalDisp isDeluxscoreNewRecord isEventMode isFastLateDisp isFreedomMode isFullCombo isHold isNewFree isPlayTutorial isSlide isTap isTouch level loginDate maxCombo maxSync musicId orderId placeId placeName playDate playMode playerNum playlogId scoreRank syncStatus totalCombo totalSync trackNo trialPlayAchievement type userPlayDate version vsMode vsRank vsStatus vsUserRating vsUserAchievement vsUserGradeRank playedMusicLevel1 playedMusicLevel2 playedMusicLevel3 extBool1 extBool2 extBool3 extNum1 extNum2 extNum4'.split()
    +[n+j for n in NOTE_TYPES for j in JUDGEMENTS]
    +[f'character{k}{i}' for i in range(1,6) for k in ('Id','Level','Awakening')])
COURSE_FIELDS='bestAchievement bestAchievementDate bestDeluxscore bestDeluxscoreDate clearDate isLastClear lastPlayDate playCount totalAchievement totalDeluxscore totalRestlife'.split()
LIST_FIELDS={
    'userPlaylogList':LOG_FIELDS,
    'userActList':'id kind param1 param2 param3 param4 sortNumber'.split(),
    'userCharacterList':'awakening characterId count favorite level nextAwake nextAwakePercent point useCount'.split(),
    'userChargeList':'chargeId stock purchaseDate validDate'.split(),
    'userCourseList':['courseId']+COURSE_FIELDS,
    'userFavoriteList':['itemKind','itemIdList'],
    'userFriendSeasonRankingList':'point rank recordDate rewardGet seasonId'.split(),
    'userItemList':'isValid itemId itemKind stock'.split(),
    'userLoginBonusList':'bonusId isComplete isCurrent point'.split(),
    'userMapList':'distance isClear isComplete isLock mapId'.split(),
    'userIntimateList':'intimateCountRewarded intimateLevel partnerId'.split(),
    'userFavoriteMusicList':['id','orderId'],
    'userKaleidxScopeList':['gateId','isClear','isGateFound','isInfoWatched','isKeyFound','totalRestLife']+[k for k in COURSE_FIELDS if k not in ('isLastClear','totalRestlife')],
    'userCardList':'cardId cardTypeId charaId mapId startDate endDate'.split(),
    'userPrintDetailList':'orderId printNumber printDate placeId cardRomVersion isHolograph printOption1 printOption2 printOption3 printOption4 printOption5 printOption6 printOption7 printOption8 printOption9 printOption10 created'.split(),
    'userRegionsList':['created','playCount','regionId'],
    'mapEncountNpcList':['npcId','musicId','mapId','difficulty','isClear'],
}
DICT_FIELDS={'userData':PROFILE_FIELDS,'userOption':OPTION_FIELDS,'userExtend':EXTEND_FIELDS,'userUdemae':UDEMAE_FIELDS}


def clean_value(value):
    if value is None or isinstance(value,(bool,int)):return value
    if isinstance(value,float):return value if math.isfinite(value) else None
    if isinstance(value,str):return value[:4096]
    # Selection/favorite lists contain primitive IDs. Do not retain arbitrary nested identities.
    if isinstance(value,list):return [clean_value(v) for v in value if v is None or isinstance(v,(str,bool,int,float))]
    return None


def parse_archive(data):
    result={'schema':1,'sections':{},'present':[],'warnings':[]}
    for name,fields in {**DICT_FIELDS,**LIST_FIELDS}.items():
        if name not in data:continue
        value=data[name];is_list=name in LIST_FIELDS
        if not isinstance(value,list if is_list else dict):
            result['warnings'].append(name+' 格式异常，未导入');continue
        result['present'].append(name)
        if not is_list:
            result['sections'][name]={k:clean_value(value[k]) for k in fields if k in value};continue
        rows=[];bad=0
        for index,row in enumerate(value):
            if not isinstance(row,dict):bad+=1;continue
            out={k:clean_value(row[k]) for k in fields if k in row}
            for key in ('comboStatus','syncStatus','itemKind'):
                if key in out and type(out[key]) is not int:out[key]=None
            if 'itemIdList' in out:
                out['itemIdList']=[v for v in out['itemIdList'] if type(v) is int and v>=0] if isinstance(out['itemIdList'],list) else []
            if name=='userPlaylogList':
                if any(isinstance(row.get(k),bool) or not isinstance(row.get(k),int) or row[k]<minimum for k,minimum in [('musicId',1),('level',0)]):bad+=1;continue
                out.update(latest_time(row,('userPlayDate','playDate'),'userPlaylogList'))
                out['sourceIndex']=index
            rows.append(out)
        result['sections'][name]=rows
        if bad:result['warnings'].append(f'{name} 跳过 {bad} 条无效记录')
    general=data.get('userGeneralDataList',[])
    if isinstance(general,list):
        selected=[{'propertyKey':r['propertyKey'],'propertyValue':str(r.get('propertyValue',''))[:100000]} for r in general if isinstance(r,dict) and r.get('propertyKey') in ('favorite_music','recent_rating','recent_rating_new','recent_rating_next','recent_rating_next_new')]
        if 'userGeneralDataList' in data:result['present'].append('userGeneralDataList');result['sections']['userGeneralDataList']=selected
    result['available']=any(name not in ('userData',) for name in result['present'])
    return result
