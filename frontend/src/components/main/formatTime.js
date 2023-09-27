function formatTime(data) {
    if (typeof data != "string")
        return;

    const date = new Date(Date.parse(data));

    let hour = new Intl.DateTimeFormat('ru', {hour: 'numeric'}).format(date);
    let minute = new Intl.DateTimeFormat('en', {minute: '2-digit'}).format(date);

    return `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`;
}

export default formatTime;