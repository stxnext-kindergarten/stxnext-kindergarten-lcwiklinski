function parseInterval(value) {
    var result = new Date(1, 1, 1);
    result.setMilliseconds(value * 1000);
    return result;
}

function avatarLoad(src, $avatar) {
    src = src || '';
    $avatar = $avatar || $('#avatar');

    return $avatar.attr('src', src);
}
