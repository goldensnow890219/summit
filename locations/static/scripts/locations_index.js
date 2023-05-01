'use strict';

import {Address, Map} from './lib/map.js';
import {Provider, Selector} from './lib/services.js';

(function() {
    // Map update on location selection
    const map = new Map(document.getElementById('map'));
    const addresses = [...document.getElementsByClassName('location-item')]
        .map((element) => new Address(element));
    addresses.forEach((address) => address.addEventListener('click', () => {
        addresses.forEach((address) => address.unselect());
        map.select(address);
    }));
    if (addresses.length > 0) {
        map.select(addresses[0]);
    }

    // Locations filtering by service
    const locations = [...document.getElementsByClassName('location-item')]
        .map((element) => new Provider(element));
    const serviceSelector = new Selector(document.getElementById('service-selector'));
    serviceSelector.addEventListener('selected', (value) => {
        locations.forEach((location) => {
            if (value === '' || location.hasService(value)) {
                location.show();
            } else {
                location.hide();
            }
        });
    });
})();