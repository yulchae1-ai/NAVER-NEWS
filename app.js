// JSON loader + mock fallback
const MOCK = {
  politics:[
    {title:'Sample Politics 1', outlet:'Mock', views:1000, comments:10, published_at:'', content:'Demo content for politics 1.'},
    {title:'Sample Politics 2', outlet:'Mock', views:900, comments:9, published_at:'', content:'Demo content for politics 2.'},
    {title:'Sample Politics 3', outlet:'Mock', views:800, comments:8, published_at:'', content:'Demo content for politics 3.'}
  ],
  economy:[
    {title:'Sample Economy 1', outlet:'Mock', views:1000, comments:10, content:'Demo content for economy 1.'},
    {title:'Sample Economy 2', outlet:'Mock', views:900, comments:9, content:'Demo content for economy 2.'},
    {title:'Sample Economy 3', outlet:'Mock', views:800, comments:8, content:'Demo content for economy 3.'}
  ],
  society:[
    {title:'Sample Society 1', outlet:'Mock', views:1000, comments:10, content:'Demo content for society 1.'},
    {title:'Sample Society 2', outlet:'Mock', views:900, comments:9, content:'Demo content for society 2.'},
    {title:'Sample Society 3', outlet:'Mock', views:800, comments:8, content:'Demo content for society 3.'}
  ],
  culture:[
    {title:'Sample Culture 1', outlet:'Mock', views:1000, comments:10, content:'Demo content for culture 1.'},
    {title:'Sample Culture 2', outlet:'Mock', views:900, comments:9, content:'Demo content for culture 2.'},
    {title:'Sample Culture 3', outlet:'Mock', views:800, comments:8, content:'Demo content for culture 3.'}
  ],
  it_science:[
    {title:'Sample IT 1', outlet:'Mock', views:1000, comments:10, content:'Demo content for IT 1.'},
    {title:'Sample IT 2', outlet:'Mock', views:900, comments:9, content:'Demo content for IT 2.'},
    {title:'Sample IT 3', outlet:'Mock', views:800, comments:8, content:'Demo content for IT 3.'}
  ]
};

const SECTION_TO_FILE = {
  politics:'outputs/politics.json',
  economy:'outputs/economy.json',
  society:'outputs/society.json',
  culture:'outputs/culture.json',
  it_science:'outputs/it_science.json'
};

const fmt = (n) => (typeof n === 'number' ? n.toLocaleString() : '-');

async function loadSection(section){
  const status = document.getElementById('status');
  status.textContent = 'Loading…';
  const file = SECTION_TO_FILE[section];
  try{
    const res = await fetch(file, {cache:'no-store'});
    if(!res.ok) throw new Error('not ok');
    const json = await res.json();
    // Normalize JSON from scraper -> [{title, url, content, ...}]
    const arr = (json || []).slice(0,3).map(d => ({
      title: d.title || '(no title)',
      outlet: d.section ? d.section.toUpperCase() : 'Naver',
      views: d.views || 0,
      comments: d.comments || 0,
      published_at: d.date || '',
      content: d.content || '',
      url: d.url || ''
    }));
    if(arr.length === 0) throw new Error('empty');
    status.textContent = 'Loaded from outputs/*.json';
    return arr;
  }catch(e){
    status.textContent = 'No JSON found — showing sample data.';
    return (MOCK[section] || []).slice(0,3);
  }
}

function renderCards(list){
  const root = document.getElementById('articles');
  root.innerHTML = list.map(a => `
    <article class="card">
      <h3>${a.title}</h3>
      <div class="meta">
        <span>📰 ${a.outlet || 'Naver'}</span>
        ${a.published_at ? `<span>📅 ${a.published_at}</span>` : ''}
      </div>
      <p>${a.content}</p>
    </article>
  `).join('');
}

function setup(){
  const buttons = document.querySelectorAll('.controls button');
  async function select(btn){
    buttons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const section = btn.dataset.cat;
    const list = await loadSection(section);
    renderCards(list);
  }
  buttons.forEach((btn, i) => {
    btn.addEventListener('click', () => select(btn));
    if(i===0) select(btn);
  });
}
document.addEventListener('DOMContentLoaded', setup);
