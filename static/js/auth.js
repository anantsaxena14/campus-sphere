function hideWarning() {
    document.getElementById('device-warning').classList.add('hidden');
}

function forceLogout() {
    const form = document.querySelector('form');
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'force_logout';
    input.value = 'true';
    form.appendChild(input);
    form.submit();
}
