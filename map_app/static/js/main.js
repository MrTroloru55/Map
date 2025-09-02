// map/map_app/static/js/main.js
// Функция для получения CSRF-токена из куки
//function getCookie(name) {
//    let cookieValue = null;
//    if (document.cookie && document.cookie !== '') {
//        const cookies = document.cookie.split(';');
//        for (let i = 0; i < cookies.length; i++) {
//            const cookie = cookies[i].trim();
//            if (cookie.startsWith(name + '=')) {
//                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                break;
//            }
//        }
//    }
//    return cookieValue;
//}

function getCSRFToken() {
    return document.querySelector('[name="csrfmiddlewaretoken"]').value;
}

document.addEventListener('DOMContentLoaded', () => {

    // Инициализация карты
    const map = L.map('map').setView([55.7558, 37.6173], 13); // Координаты Москвы

    // Добавление слоя OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Слой для хранения нарисованных объектов
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Настройка панели инструментов для рисования
    const drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polygon: true,
            polyline: true,
            rectangle: false,
            circle: false,
            marker: true,
            circlemarker: false,
        }
    });
    map.addControl(drawControl);

    // Добавление GeoJSON объектов на карту
    function addGeoJSONToMap(geojson) {
        L.geoJSON(geojson, {
            onEachFeature: function (feature, layer) {
                // Создание всплывающего окна с информацией об объекте
                let popupContent = `
                    <h4>${feature.properties.name || 'Название не указано'}</h4>
                    <p>${feature.properties.description || 'Описание не указано'}</p>
                `;
                
                if (feature.properties.photo_url) {
                    popupContent += `<img src="${feature.properties.photo_url}" style="max-width:200px; max-height:200px;">`;
                }

                popupContent += `<hr><button onclick="addPhoto('${feature.id}')">Добавить фото</button>`;

                layer.bindPopup(popupContent);
            }
        }).addTo(map);
    }

    // Загрузка объектов из базы данных при загрузке страницы
    fetch('/api/map_objects/get/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Не удалось загрузить данные карты');
            }
            return response.json();
        })
        .then(data => {
            console.log('Загруженные данные:', data);
            addGeoJSONToMap(data);
        })
        .catch(error => console.error('Ошибка:', error));

    // Обработчик события, когда пользователь закончил рисовать объект
    map.on(L.Draw.Event.CREATED, function (e) {
        const layer = e.layer;
        const geojson = layer.toGeoJSON();
        drawnItems.addLayer(layer);

        // Отправка GeoJSON данных на сервер Django
        const csrftoken = getCSRFToken();
        fetch('/api/map_objects/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(geojson),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(JSON.stringify(err)); });
            }
            return response.json();
        })
        .then(data => {
            console.log('Успешно сохранено:', data);
            // Можно обновить карту, чтобы отобразить новый объект
            // Обычно, если есть другие пользователи, лучше перезагрузить все данные
            // Но для простоты мы просто добавим новый объект
        })
        .catch(error => {
            console.error('Ошибка при сохранении:', error);
            alert('Ошибка при сохранении объекта: ' + error.message);
        });
    });

    // Функция-плейсхолдер для добавления фото
    window.addPhoto = function(featureId) {
        alert(`Функционал добавления фото для объекта с ID ${featureId} пока не реализован.`);
        // Здесь можно было бы открыть модальное окно с формой загрузки
    };
});