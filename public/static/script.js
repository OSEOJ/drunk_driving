document.addEventListener("DOMContentLoaded", function () {
  const snapContainer = document.getElementById('snap-container');
  const faders = document.querySelectorAll('.fade-in');
  const appearOptions = { 
    threshold: 0.2,
    root: snapContainer
  };
  
  const appearOnScroll = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('appear');
        observer.unobserve(entry.target);
      }
    });
  }, appearOptions);
  
  faders.forEach(fader => appearOnScroll.observe(fader));
  
  function checkInitialFadeIn() {
    faders.forEach(fader => {
      if (fader.getBoundingClientRect().top < window.innerHeight * 0.85) {
        fader.classList.add('appear');
      }
    });
  }
  checkInitialFadeIn();
  
  // 동적 주류 입력 관련 (기존 그대로)
  const beverageConversions = {
    "소주": { bottle: 360, glass: 48 },
    "맥주": { bottle: 500, glass: 200 },
    "막걸리": { bottle: 750, glass: 300 },
    "양주": { bottle: 750, glass: 30 },
    "와인": { bottle: 750, glass: 125 }
  };
  
  const beverageCheckboxes = document.querySelectorAll('input[name="beverageCheckbox"]');
  const beverageDetailsContainer = document.getElementById("beverageDetailsContainer");
  
  beverageCheckboxes.forEach(checkbox => {
    checkbox.addEventListener("change", function() {
      const bev = this.value;
      if (this.checked) {
        addBeverageBlock(bev);
      } else {
        removeBeverageBlock(bev);
      }
    });
  });
  
  function addBeverageBlock(bev) {
    if (document.querySelector(`.beverage-block[data-bev="${bev}"]`)) return;
    const block = document.createElement("div");
    block.className = "beverage-block";
    block.setAttribute("data-bev", bev);
    block.innerHTML = `
      <h3>${bev}</h3>
      <div>
        <label for="alcoholContent_${bev}">알코올 도수 (%):</label>
        <input type="number" id="alcoholContent_${bev}" placeholder="예: 20" required>
      </div>
      <div>
        <label>음료량 선택:</label>
        <div>
          <input type="radio" name="volumeType_${bev}" value="bottle" id="vol_bottle_${bev}" checked>
          <label for="vol_bottle_${bev}">병 수</label>
          <input type="radio" name="volumeType_${bev}" value="glass" id="vol_glass_${bev}">
          <label for="vol_glass_${bev}">잔 수</label>
          <input type="radio" name="volumeType_${bev}" value="direct" id="vol_direct_${bev}">
          <label for="vol_direct_${bev}">직접 ml 입력</label>
        </div>
      </div>
      <div class="volume-input" id="volumeInput_${bev}">
        <div class="bottleInput">
          <label for="bottleCount_${bev}">병 수:</label>
          <input type="number" id="bottleCount_${bev}" name="bottleCount_${bev}" placeholder="예: 1">
        </div>
        <div class="glassInput" style="display:none;">
          <label for="glassCount_${bev}">잔 수:</label>
          <input type="number" id="glassCount_${bev}" name="glassCount_${bev}" placeholder="예: 2">
        </div>
        <div class="directInput" style="display:none;">
          <label for="directML_${bev}">ml:</label>
          <input type="number" id="directML_${bev}" name="directML_${bev}" placeholder="예: ${beverageConversions[bev].bottle}">
        </div>
      </div>
      <div class="conversion-info" id="conversionInfo_${bev}">
        <p>${bev}: 1병 = ${beverageConversions[bev].bottle}ml, 1잔 = ${beverageConversions[bev].glass}ml</p>
      </div>
    `;
    beverageDetailsContainer.appendChild(block);
  
    const volumeRadios = block.querySelectorAll(`input[name="volumeType_${bev}"]`);
    volumeRadios.forEach(radio => {
      radio.addEventListener("change", function() {
        updateVolumeInput(bev);
      });
    });
  }
  
  function removeBeverageBlock(bev) {
    const block = document.querySelector(`.beverage-block[data-bev="${bev}"]`);
    if (block) {
      block.remove();
    }
  }
  
  function updateVolumeInput(bev) {
    const block = document.querySelector(`.beverage-block[data-bev="${bev}"]`);
    if (!block) return;
    const selected = block.querySelector(`input[name="volumeType_${bev}"]:checked`).value;
    const bottleInput = block.querySelector(".bottleInput");
    const glassInput = block.querySelector(".glassInput");
    const directInput = block.querySelector(".directInput");
    if (selected === "bottle") {
      bottleInput.style.display = "block";
      glassInput.style.display = "none";
      directInput.style.display = "none";
    } else if (selected === "glass") {
      bottleInput.style.display = "none";
      glassInput.style.display = "block";
      directInput.style.display = "none";
    } else if (selected === "direct") {
      bottleInput.style.display = "none";
      glassInput.style.display = "none";
      directInput.style.display = "block";
    }
  }
  
  // 폼 제출 처리 (입력폼은 좌측에 유지되고, 우측 그래프 영역에 결과 업데이트)
  const form = document.getElementById("userInputForm");
  if (form) {
    form.addEventListener("submit", function(event) {
      event.preventDefault();
      const formData = new FormData(form);
      fetch("/custom_calculate", {
        method: "POST",
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        const resultHTML = `
          <h2>측정 결과</h2>
          <p>총 알콜 섭취량: ${data.total_alcohol.toFixed(2)} g</p>
          <p>마신 직후 BAC: ${data.initial_bac.toFixed(3)}%</p>
          <p>음주 후 BAC: ${data.bac.toFixed(3)}%</p>
          <div class="penalty-display">처벌 기준: ${data.penalty}</div>
          <ul>
            ${data.details.map(item => `<li>${item}</li>`).join('')}
          </ul>
          <img src="${data.graph_url}?t=${new Date().getTime()}" alt="BAC Graph">
        `;
        document.getElementById("graphContainer").innerHTML = resultHTML;
        document.getElementById("graphContainer").style.display = "block";
      })
      .catch(err => console.error("Error:", err));
    });
  }
});