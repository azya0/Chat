function scrollHandler(event) {
    let element = document.getElementById('scroller');

    if (event.target.scrollTop < -100) {
        if (element.style.visibility !== 'visible') {
            element.style.visibility = "visible";
            element.style.opacity = 1;
        }
    } else if (element.style.visibility === 'visible') {
        element.style.visibility = "hidden";
        element.style.opacity = 0;
    }
}

export default scrollHandler;