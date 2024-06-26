from decouple import config

from chalicelib.utils.storage import StorageClient


def __get_mob_keys(project_id, session_id):
    params = {
        "sessionId": session_id,
        "projectId": project_id
    }
    return [
        config("SESSION_MOB_PATTERN_S", default="%(sessionId)s") % params,
        config("SESSION_MOB_PATTERN_E", default="%(sessionId)se") % params
    ]


def __get_mobile_video_keys(project_id, session_id):
    params = {
        "sessionId": session_id,
        "projectId": project_id
    }
    return [
        config("SESSION_IOS_VIDEO_PATTERN") % params,
    ]


def __get_mob_keys_deprecated(session_id):
    return [str(session_id), str(session_id) + "e"]


def get_first_url(project_id, session_id, check_existence: bool = True):
    k = __get_mob_keys(project_id=project_id, session_id=session_id)[0]
    if check_existence and not StorageClient.exists(bucket=config("sessions_bucket"), key=k):
        return None
    return StorageClient.get_presigned_url_for_sharing(
        bucket=config("sessions_bucket"),
        expires_in=config("PRESIGNED_URL_EXPIRATION", cast=int, default=900),
        key=k
    )


def get_urls(project_id, session_id, check_existence: bool = True):
    results = []
    for k in __get_mob_keys(project_id=project_id, session_id=session_id):
        if check_existence and not StorageClient.exists(bucket=config("sessions_bucket"), key=k):
            continue
        results.append(StorageClient.get_presigned_url_for_sharing(
            bucket=config("sessions_bucket"),
            expires_in=config("PRESIGNED_URL_EXPIRATION", cast=int, default=900),
            key=k
        ))
    return results


def get_urls_depercated(session_id, check_existence: bool = True):
    results = []
    for k in __get_mob_keys_deprecated(session_id=session_id):
        if check_existence and not StorageClient.exists(bucket=config("sessions_bucket"), key=k):
            continue
        results.append(StorageClient.get_presigned_url_for_sharing(
            bucket=config("sessions_bucket"),
            expires_in=100000,
            key=k
        ))
    return results


def get_mobile_videos(session_id, project_id, check_existence=False):
    results = []
    for k in __get_mobile_video_keys(project_id=project_id, session_id=session_id):
        if check_existence and not StorageClient.exists(bucket=config("IOS_VIDEO_BUCKET"), key=k):
            continue
        results.append(StorageClient.get_presigned_url_for_sharing(
            bucket=config("IOS_VIDEO_BUCKET"),
            expires_in=config("PRESIGNED_URL_EXPIRATION", cast=int, default=900),
            key=k
        ))
    return results


def get_audio_url(project_id, session_id, check_existence=True):
    k = "%s/audio.mp3" % session_id
    if check_existence and not StorageClient.exists(bucket=config("sessions_bucket"), key=k):
        return None
    return StorageClient.get_presigned_url_for_sharing(
        bucket=config("sessions_bucket"),
        expires_in=config("PRESIGNED_URL_EXPIRATION", cast=int, default=900),
        key=k
    )


def delete_mobs(project_id, session_ids):
    for session_id in session_ids:
        for k in __get_mob_keys(project_id=project_id, session_id=session_id) \
                 + __get_mob_keys_deprecated(session_id=session_id):
            StorageClient.tag_for_deletion(bucket=config("sessions_bucket"), key=k)
