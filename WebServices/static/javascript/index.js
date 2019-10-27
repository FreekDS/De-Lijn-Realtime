function hideJson(to_hide) {
            let json = document.getElementById(to_hide);
            console.log(json.style.display);
            if (json.style.display === 'none' || json.style.display === "")
                json.style.display = 'flex';
            else
                json.style.display = 'none';
        }
