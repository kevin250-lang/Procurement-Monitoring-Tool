document.getElementById("demoa").onchange = evt => {

    // NEW FILE READER
    var reader = new FileReader();

    // ON FINISH LOADING
    reader.addEventListener("loadend",evt=>{
        // GET HTML TABLE
        var table = document.getElementById("demob")
        table.innerHTML = "";

        // GET THE FIRST WORKSHEET
        var workbook = XLSX.read(evt.currentTarget.result, {type:"binary"}),
        worksheet = workbook.Sheets[workbook.SheetNames[0]],
        range = XLSX.utils.decode_range(worksheet["!ref"]);

        for (let row=ranges.s.r; row<=range.e.r; row++){
            let r = table.insertRow();
            for (let col=range.s.c; col<=range.e.c; col++){
                let c = r.insertCell(),
                xcell = worksheet[XLSX.utils.encode_cell({r:row, c:col})];
                c.innertHTML = xcell.v;
            }

        }
    });

    // START - READ SELECTED EXCEL FILE
    reader.readAsArrayBuffer(evt.target.files[0])
};