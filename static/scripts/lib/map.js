'use strict';

class Address {
    constructor(element) {
        this.element = element;
    }

    getAddress() {
        return this.element.dataset.address;
    }

    addEventListener(eventName, func) {
        this.element.addEventListener(eventName, () => func());
    }

    select() {
        this.element.classList.add('selected');
    }

    unselect() {
        this.element.classList.remove('selected');
    }
}

class Map {
    constructor(element) {
        this.element = element;
    }

    select(address) {
        const url = `https://maps.google.com/maps?hl=en&q=${encodeURI(address.getAddress())}&t=&z=16&ie=UTF8&iwloc=B&output=embed`;
        if (this.element.src !== url) {
            this.element.src = url;
        }
        address.select()
    }
}

export {Address, Map};
