const gotostep = document.getElementById('gotostep');
if (gotostep) {
    const button = document.getElementById('btn_gotostep');
    gotostep.addEventListener('change', function () {
        button.href = button.href.replace(/step=[^&]*/, 'step=' + gotostep.value);
    })
}

const url = new URL(location.href);
const params = url.searchParams;
const key = 'record'
const key1 = 'record2'
const rec = params.get(key)
const rec1 = params.get(key1)
const records = document.querySelectorAll('form.record');
for (const record of records) {
    const name = record.querySelector('input.name');
    const _value = name.value;
    const _class = name.className;
    name.addEventListener('change', function () {
        if (_value !== name.value)
            name.className = _class + ' bg-warning';
        else
            name.className = _class;
    })

    const load = record.querySelector('a.load');
    if (load) {
        if (rec === record.id || rec1 === record.id) {
            load.className = load.className.replace('load', 'unload');
            load.className = load.className.replace('btn-outline-secondary', 'btn-outline-primary');
            load.innerHTML = load.innerHTML.replace('Load', 'Unload');
        }
        load.addEventListener('click', function () {
            if (rec === record.id)
                params.delete(key)
            else if (rec1 === record.id)
                params.delete(key1);
            else if (rec === null)
                params.set(key, record.id);
            else if (rec1 === null)
                params.set(key1, record.id);
            location.href = url.toString();
        })
    }
}

const header = document.getElementById('header')
const footer = document.getElementById('footer')
if (header && footer) {
    document.body.style.marginTop = header.clientHeight + 'px'
    document.body.style.marginBottom = footer.clientHeight + 'px'
    window.addEventListener('resize', function () {
        document.body.style.marginTop = header.clientHeight + 'px'
        document.body.style.marginBottom = footer.clientHeight + 'px'
    })
}