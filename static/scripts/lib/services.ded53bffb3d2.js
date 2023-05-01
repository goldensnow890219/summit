'use strict';

class Provider {
    constructor(element) {
        this.element = element;
        this.services = element.dataset.services.split(',');
        this.display = {
            value: element.style.getPropertyValue('display'),
            priority: element.style.getPropertyPriority('display'),
        };
    }

    hasService(service) {
        return this.services.indexOf(service) !== -1;
    }

    hide() {
        this.element.style.setProperty('display', 'none', 'important');
    }

    show() {
        this.element.style.setProperty('display', this.display.value, this.display.priority);
    }
}

class Selector {
    constructor(element) {
        this.element = element;
        this.events = {
            selected: [],
        }
        this.service = '';
        this.element.onchange = (event) => this.onSelected(event);
    }

    onSelected(event) {
        this.events.selected.forEach(func => func(this.element.value));
    }

    addEventListener(eventName, func) {
        if(this.events.hasOwnProperty(eventName)) {
            this.events[eventName].push(func);
        } else {
            throw `Unknown event ${eventName}`;
        }
    }

    select(index) {
        if (index < this.element.children.length) {
            this.element.children[index].selected = true;
            this.element.dispatchEvent(new Event('onchange'));
        }
    }
}

class Counter {
    constructor(element, count) {
        this.element = element;
        this.count = count;
    }

    add(value) {
       this.count += value;
       this.element.innerText = `${this.count}`
    }
}

export {Provider, Selector, Counter};
