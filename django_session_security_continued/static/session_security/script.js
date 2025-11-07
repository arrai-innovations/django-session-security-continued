(function (globalWindow, globalDocument) {
    "use strict";

    if (typeof globalWindow.yourlabs === "undefined") {
        globalWindow.yourlabs = {};
    }

    function assign(target, source) {
        if (!source) {
            return target;
        }
        Object.keys(source).forEach(function (key) {
            target[key] = source[key];
        });
        return target;
    }

    function buildUrl(url, params) {
        let hasQuery = url.indexOf("?") !== -1;
        let query = [];
        for (let key in params) {
            if (Object.prototype.hasOwnProperty.call(params, key)) {
                query.push(encodeURIComponent(key) + "=" + encodeURIComponent(params[key]));
            }
        }
        return url + (hasQuery ? "&" : "?") + query.join("&");
    }

    function hasDirtyForms() {
        return globalDocument.querySelector("form[data-dirty]") !== null;
    }

    function SessionSecurity(options) {
        this.warning = globalDocument.getElementById("session_security_warning");
        this.warningVisible = false;
        this.lastActivity = new Date();
        this.events = [
            "mousemove",
            "scroll",
            "keyup",
            "click",
            "touchstart",
            "touchend",
            "touchmove",
        ];
        this.counterElementID = "session_security_counter";
        this.expired = false;
        this.counterStarted = false;
        this.timeout = null;
        this.counterTimeout = null;

        assign(this, options || {});

        let self = this;
        this.activityHandler = this.activity.bind(this);
        this.events.forEach(function (eventName) {
            globalDocument.addEventListener(eventName, self.activityHandler, true);
        });

        if (this.confirmFormDiscard) {
            this.beforeUnloadHandler = this.onbeforeunload.bind(this);
            globalWindow.addEventListener("beforeunload", this.beforeUnloadHandler);
            globalDocument.addEventListener(
                "change",
                function (event) {
                    self.formChange(event);
                },
                true,
            );
            globalDocument.addEventListener(
                "submit",
                function (event) {
                    self.formClean(event);
                },
                true,
            );
            globalDocument.addEventListener(
                "reset",
                function (event) {
                    self.formClean(event);
                },
                true,
            );
        }

        this.apply();
    }

    SessionSecurity.prototype.expire = function () {
        if (this.expired) {
            return;
        }
        this.expired = true;
        if (typeof this.returnToUrl === "string" && this.returnToUrl.length > 0) {
            globalWindow.location.href = this.returnToUrl;
        } else {
            globalWindow.location.reload();
        }
    };

    SessionSecurity.prototype.showWarning = function () {
        if (!this.warning) {
            return;
        }
        this.warning.style.display = "block";
        this.warning.setAttribute("aria-hidden", "false");
        this.warningVisible = true;
        let modal = this.warning.querySelector(".session_security_modal");
        if (modal && typeof modal.focus === "function") {
            modal.focus();
        }
    };

    SessionSecurity.prototype.hideWarning = function () {
        if (!this.warning) {
            return;
        }
        this.warning.style.display = "none";
        this.warning.setAttribute("aria-hidden", "true");
        this.warningVisible = false;
    };

    SessionSecurity.prototype.activity = function () {
        let now = new Date();
        if (now - this.lastActivity < 1000) {
            return;
        }

        let idleFor = Math.floor((now - this.lastActivity) / 1000);
        this.lastActivity = now;

        if (idleFor >= this.expireAfter) {
            this.expire();
            return;
        }

        if (this.warningVisible) {
            this.ping();
            this.hideWarning();
        }
    };

    SessionSecurity.prototype.ping = function () {
        let idleFor = Math.floor((new Date() - this.lastActivity) / 1000);
        let self = this;

        fetch(buildUrl(this.pingUrl, { idleFor: idleFor }), {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                self.pong(data);
            })
            .catch(function () {
                self.apply();
            });
    };

    SessionSecurity.prototype.pong = function (data) {
        if (data === "logout") {
            this.expire();
            return;
        }

        this.lastActivity = new Date();
        this.lastActivity.setSeconds(this.lastActivity.getSeconds() - data);
        this.apply();
    };

    SessionSecurity.prototype.apply = function () {
        clearTimeout(this.timeout);
        let idleFor = Math.floor((new Date() - this.lastActivity) / 1000);
        let nextPing;

        if (idleFor >= this.expireAfter) {
            this.expire();
            return;
        } else if (idleFor >= this.warnAfter) {
            if (!this.counterStarted && this.counterElementID) {
                this.startCounter();
            }
            this.showWarning();
            nextPing = this.expireAfter - idleFor;
        } else {
            this.hideWarning();
            if (this.counterStarted && this.counterElementID) {
                this.stopCounter();
            }
            nextPing = this.warnAfter - idleFor;
        }

        let milliseconds = Math.min(nextPing * 1000, 2147483647);
        let self = this;
        this.timeout = setTimeout(function () {
            self.ping();
        }, milliseconds);
    };

    SessionSecurity.prototype.startCounter = function () {
        if (!this.counterElementID) {
            return;
        }
        let element = globalDocument.getElementById(this.counterElementID);
        if (!element) {
            return;
        }
        let expireAfter = this.expireAfter;
        let warnAfter = this.warnAfter;
        let defaultTimeLeft = expireAfter - warnAfter;

        if (!this.counterStarted) {
            element.textContent = defaultTimeLeft.toString();
            this.counterStarted = true;
        }

        let endTime = new Date();
        endTime.setSeconds(endTime.getSeconds() + defaultTimeLeft);
        this.counterTimeout = setInterval(function () {
            let now = new Date().getTime();
            let distance = endTime - now;
            let seconds = Math.max(0, Math.floor((distance % (1000 * expireAfter)) / 1000));
            if (distance > 0) {
                element.textContent = seconds.toString();
            }
        }, 1000);
    };

    SessionSecurity.prototype.stopCounter = function () {
        if (!this.counterElementID) {
            return;
        }
        let element = globalDocument.getElementById(this.counterElementID);
        if (!element) {
            return;
        }
        clearInterval(this.counterTimeout);
        this.counterStarted = false;
        let defaultTimeLeft = this.expireAfter - this.warnAfter;
        element.textContent = defaultTimeLeft.toString();
    };

    SessionSecurity.prototype.onbeforeunload = function (event) {
        if (this.expired || !this.confirmFormDiscard) {
            return undefined;
        }
        if (hasDirtyForms()) {
            event.preventDefault();
            event.returnValue = this.confirmFormDiscard;
            return this.confirmFormDiscard;
        }
        return undefined;
    };

    SessionSecurity.prototype.formChange = function (event) {
        if (!event.target || typeof event.target.closest !== "function") {
            return;
        }
        let form = event.target.closest("form");
        if (form) {
            form.setAttribute("data-dirty", "true");
        }
    };

    SessionSecurity.prototype.formClean = function (event) {
        if (!event.target || typeof event.target.closest !== "function") {
            return;
        }
        let form = event.target.closest("form");
        if (form) {
            form.removeAttribute("data-dirty");
        }
    };

    globalWindow.yourlabs.SessionSecurity = SessionSecurity;
})(window, document);
