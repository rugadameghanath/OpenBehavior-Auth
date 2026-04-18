// OBA Collector - Captures the "Rhythm" of the user
const OBA = {
    data: {
        dwells: [],
        flights: [],
        lastKeyUp: 0
    },

    init: function(elementId) {
        const target = document.getElementById(elementId);
        
        target.addEventListener('keydown', (e) => {
            const now = performance.now();
            
            // Calculate Flight Time (Gap between keys)
            if (this.data.lastKeyUp > 0) {
                this.data.flights.push(now - this.data.lastKeyUp);
            }
            
            // Mark the start of the press
            target.dataset.pressStart = now;
        });

        target.addEventListener('keyup', (e) => {
            const now = performance.now();
            const start = parseFloat(target.dataset.pressStart);
            
            // Calculate Dwell Time (How long key was held)
            if (start) {
                this.data.dwells.push(now - start);
            }
            this.data.lastKeyUp = now;
        });
    },

    // The "Export" function to send data to your SQL DB later
    getSummary: function() {
        const avg = arr => arr.length ? arr.reduce((a,b) => a+b)/arr.length : 0;
        return {
            avg_dwell: avg(this.data.dwells).toFixed(2),
            avg_flight: avg(this.data.flights).toFixed(2),
            key_count: this.data.dwells.length
        };
    }
};

// Usage: OBA.init('password_field_id');
