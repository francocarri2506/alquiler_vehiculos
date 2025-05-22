const provinciasURL = "https://apis.datos.gob.ar/georef/api/provincias";
const departamentosURL = "https://apis.datos.gob.ar/georef/api/departamentos";
const localidadesURL = "https://apis.datos.gob.ar/georef/api/localidades";

const provinciaSelect = document.getElementById("provincia");
const departamentoSelect = document.getElementById("departamento");
const localidadSelect = document.getElementById("localidad");

document.addEventListener("DOMContentLoaded", () => {
    fetch(provinciasURL)
        .then(response => response.json())
        .then(data => {
            data.provincias.forEach(p => {
                const option = document.createElement("option");
                option.value = p.nombre;
                option.textContent = p.nombre;
                provinciaSelect.appendChild(option);
            });
        });
});

provinciaSelect.addEventListener("change", () => {
    const prov = provinciaSelect.value;
    departamentoSelect.innerHTML = '<option selected disabled>Seleccione un departamento</option>';
    localidadSelect.innerHTML = '<option selected disabled>Seleccione una localidad</option>';
    fetch(`${departamentosURL}?provincia=${prov}&max=1000`)
        .then(response => response.json())
        .then(data => {
            data.departamentos.forEach(d => {
                const option = document.createElement("option");
                option.value = d.nombre;
                option.textContent = d.nombre;
                departamentoSelect.appendChild(option);
            });
        });
});

departamentoSelect.addEventListener("change", () => {
    const prov = provinciaSelect.value;
    const depto = departamentoSelect.value;
    localidadSelect.innerHTML = '<option selected disabled>Seleccione una localidad</option>';
    fetch(`${localidadesURL}?provincia=${prov}&departamento=${depto}&max=1000`)
        .then(response => response.json())
        .then(data => {
            data.localidades.forEach(l => {
                const option = document.createElement("option");
                option.value = l.nombre;
                option.textContent = l.nombre;
                localidadSelect.appendChild(option);
            });
        });
});

document.getElementById("sucursalForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const data = {
        nombre: this.nombre.value,
        provincia: this.provincia.value,
        departamento: this.departamento.value,
        localidad: this.localidad.value,
        direccion: this.direccion.value
    };

    fetch("/api/v1/viewset/sucursales/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(data)
    })
        .then(resp => {
            if (resp.ok) {
                return resp.json();
            }
            return resp.json().then(err => {
                throw err;
            });
        })
        .then(result => {
            document.getElementById("respuesta").textContent = "Sucursal guardada exitosamente.";
            document.getElementById("sucursalForm").reset();
        })
        .catch(error => {
            document.getElementById("respuesta").textContent = "Error: " + JSON.stringify(error);
        });
});

// Función auxiliar para obtener el CSRF token desde las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // ¿Este cookie es el que queremos?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}