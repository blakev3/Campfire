
setTimeout(removeLoader, 500);

function removeLoader() {
    const preloader = document.getElementById("loader");
    const parent = preloader.parentElement;
    parent.removeChild(preloader);
}

function setupClickableElements() {
    var clickableElements = document.querySelectorAll('a, button, [role="button"]');
    clickableElements.forEach(function(element) {
        element.addEventListener('mouseover', function() {
            var rotation = Math.random() * 10 - 5; // Random number between -5 and 5
            this.style.setProperty('transform', 'scale(1.1) rotate(' + rotation + 'deg)', 'important');
        });
        element.addEventListener('mouseout', function() {
            this.style.setProperty('transform', '', 'important');
        });
    });
}

function showIdleAlert() {
    // Create an overlay element
    let overlay = document.createElement('div');
    overlay.setAttribute('id', 'overlay');

    // Create a h1 element
    let h1 = document.createElement('h1');
    h1.setAttribute('id', 'idleTime');

    // Create a marquee element
    marquee1 = document.createElement('marquee');
    marquee1.setAttribute('direction', 'down');
    marquee1.setAttribute('width', '250');
    marquee1.setAttribute('height', '200');
    marquee1.setAttribute('behavior', 'alternate');
    marquee1.setAttribute('style', 'border:solid');
    marquee1.setAttribute('class', 'marquee');

    let marquee2 = document.createElement('marquee');
    marquee2.setAttribute('behavior', 'alternate');
    marquee2.textContent = 'Screensaver';

    // Append the second marquee to the first one
    marquee1.appendChild(marquee2);

    // Append the first marquee, the h1 and the overlay to the body of the document
    document.body.appendChild(overlay);
    document.body.appendChild(h1);
    document.body.appendChild(marquee1);

    // Update the h1 text every second
    setInterval(function() {
        let idleSeconds = Math.floor((Date.now() - startTime) / 1000);
        h1.textContent = "You have been idle for " + idleSeconds + " seconds";
    }, 1000);
}

function resetTimer() {
    clearTimeout(idleTime);

    // Remove the marquee, h1 and overlay if they exist
    let overlay = document.getElementById('overlay');
    let h1 = document.getElementById('idleTime');

    if (marquee1) {
        document.body.removeChild(marquee1);
        document.body.removeChild(h1);
        document.body.removeChild(overlay);
        marquee1 = null;
        startTime = Date.now();
    }

    idleTime = setTimeout(showIdleAlert, 60000); // 60000 milliseconds = 1 minute
}

window.onload = function() {
    setupClickableElements();
    resetTimer();
};

$(document).ready(function() {
    $('#title').keyup(function() {
        var charCount = $(this).val().length;
        $('#wordCount').text(charCount + '/20');
    });

    $('#description').keyup(function() {
        var charCount = $(this).val().length;
        $('#wordCount').text(charCount + '/200');
    });

    $('#content').keyup(function() {
        var charCount = $(this).val().length;
        $('#wordCount').text(charCount + '/2000');
    });

    $('textarea').on('input', function() {
        var charCount = $(this).val().length;
        var maxChars = $(this).attr('maxlength');
        var wordCountElement = $(this).siblings('.word-count');
        wordCountElement.text(charCount + '/' + maxChars);
    });
});

window.onload = function() {
    setupClickableElements();
    resetTimer();
};
