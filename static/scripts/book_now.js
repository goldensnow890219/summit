'use strict';

import {Counter, Provider, Selector} from "./lib/services.js";

(function() {
    const professionals = [...document.getElementsByClassName('result-list')]
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
    serviceSelector.select(1);
})();