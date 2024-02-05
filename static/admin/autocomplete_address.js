document.addEventListener('DOMContentLoaded', function () {
    const cepInput = document.getElementById('id_cep');
    const streetInput = document.getElementById('id_street');
    const complementInput = document.getElementById('id_complement');
    const neighborhoodInput = document.getElementById('id_neighborhood');
    const cityInput = document.getElementById('id_city');
    const stateInput = document.getElementById('id_state');

    cepInput.addEventListener('blur', function () {
        const cep = this.value.replace(/\D/g, '');

        if (cep != "") {
            const validacep = /^[0-9]{8}$/;

            if(validacep.test(cep)) {
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!("erro" in data)) {
                            streetInput.value = data.logradouro;
                            complementInput.value = data.complemento;
                            neighborhoodInput.value = data.bairro;
                            cityInput.value = data.localidade;
                            stateInput.value = data.uf;
                        } else {
                            alert("CEP não encontrado.");
                        }
                    })
                    .catch(() => {
                        alert("Erro ao buscar CEP. Por favor, tente novamente.");
                    });
            } else {
                alert("Formato de CEP inválido.");
            }
        }
    });
});