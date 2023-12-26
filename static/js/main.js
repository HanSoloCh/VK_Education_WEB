function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function handleLikeClick(itemId, itemType, likeType) {
    const formData = new FormData();
    formData.append(`${itemType}_id`, itemId);
    formData.append('like_type', likeType);

    const request = new Request(`/${itemType}_like/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    });

    fetch(request)
        .then((response) => response.json())
        .then((data) => {
            const counter = document.querySelector(`[data-id="${itemId}"]`);
            counter.innerHTML = data.count;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function attachLikeHandlers(items, itemType) {
    for (let item of items) {
        const [like, counter, dislike] = item.children;

        like.addEventListener('click', () => handleLikeClick(counter.dataset.id, itemType, 'like'));
        dislike.addEventListener('click', () => handleLikeClick(counter.dataset.id, itemType, 'dislike'));
    }
}

const questionItems = document.getElementsByClassName('question-reputation');
const answerItems = document.getElementsByClassName('answer-reputation');

attachLikeHandlers(questionItems, 'question');
attachLikeHandlers(answerItems, 'answer');

function makeCorrect(itemId) {
    const formData = new FormData();
    formData.append('answer_id', itemId);

    const request = new Request('/make_correct/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    });

    fetch(request)
        .then((response) => response.json())
        .then((data) => {

            // Обновление интерфейса после успешного ответа от сервера
            console.log(data);
            const label = document.querySelector(`[data-id="${itemId}"] .form-check-label`);
            console.log(label);
            if (data.correct)
                label.innerHTML = "Правильный ответ.";
            else
                label.innerHTML = "Отметить как правильный.";

        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

const correctButtons = document.getElementsByClassName('correct-answer');

for (let item of correctButtons) {
    const button = item.children[0];

    button.addEventListener('click', () => makeCorrect(item.dataset.id));
}


