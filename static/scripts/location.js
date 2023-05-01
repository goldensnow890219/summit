'use strict';

import {Counter, Provider, Selector} from './lib/services.js'
import {Address, Map} from "./lib/map.js";    // Map loader

(function() {
    // Update map with current location address
    const address = new Address(document.getElementById('location-address'));
    const map = new Map(document.getElementById('map'));
    map.select(address);

    // Professionals filtering by service
    const professionals = [...document.querySelectorAll('.profile-item')]
        .map((element) => new Provider(element));
    const serviceSelector = new Selector(document.getElementById('service-selector'));
    serviceSelector.addEventListener('selected', (value) => {
        const counter = new Counter(document.getElementById('count'), 0);
        professionals.forEach(professional => {
            if (value === '' || professional.hasService(value)) {
                professional.show();
                counter.add(1);
            } else {
                professional.hide();
            }
        });
    });
})();
