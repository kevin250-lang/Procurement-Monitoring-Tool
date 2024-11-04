const modalBtns = [...document.getElementsByClassName('modal-button')]
const modalBody = document.getElementById('modal-body-confirm')
const startBtn  = document.getElementById('start-button')
const url = window.location.href
 
modalBtns.forEach(modalBtn=> modalBtn.addEventListener('click',()=>{
    const name= modalBtn.getAttribute('data-name')
    const pk= modalBtn.getAttribute('data-pk')
    const topic= modalBtn.getAttribute('data-topic')
    const numQuestions= modalBtn.getAttribute('data-questions')
    const time= modalBtn.getAttribute('data-time')
    const scoreToPass= modalBtn.getAttribute('data-pass')

    modalBody.innerHTML = `
    <div class="h5 mb-3" >Are you sure you want to begin "<b>${name}</b>?</div>
    <div class="text-muted">
        <ul>
            <li>Name: <b>${name}</b></li>
            <li>Number of questions: <b>${numQuestions}</b></li>
            <li>Score to pass: <b>${scoreToPass}%</b></li>
            <li>Time: <b>${time} min</b></li>
        </ul>
    </div>
    `

    startBtn.addEventListener('click',()=>{
        window.location.href = url + pk
    })
}))