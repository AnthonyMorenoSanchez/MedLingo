import {test,expect} from '@playwright/test';
test.beforeEach(async({page})=>{await page.addInitScript(()=>localStorage.setItem('medlingo.profile','1'))});
test.beforeEach(async({page})=>{await page.addInitScript(()=>{(window as any).__spoken=[];Object.defineProperty(window,'speechSynthesis',{value:{getVoices:()=>[{name:'Spanish',lang:'es-MX',localService:true},{name:'English',lang:'en-US',localService:true}],speak:(u:any)=>(window as any).__spoken.push({text:u.text,lang:u.lang}),cancel:()=>{},addEventListener:()=>{},removeEventListener:()=>{}}});(window as any).SpeechSynthesisUtterance=class{text:string;constructor(text:string){this.text=text}lang='';rate=1;voice=null}})});
test('study, hints, give up, dashboard, review, wrong-only test',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');await expect(page.locator('.hero h1')).toContainText('A little practice.');await page.screenshot({path:'../data/home-preview.png',fullPage:true});
 await page.goto('/study/setup?specialty=urology');await page.getByLabel('Questions',{exact:true}).fill('10');
 const response=page.waitForResponse(r=>r.url().endsWith('/api/sessions')&&r.request().method()==='POST');await page.getByRole('button',{name:'Let’s practice'}).click();const batch=await (await response).json();
 const kinds=new Set<string>();
 for(let i=0;i<10;i++){
  const item=batch.items[i];kinds.add(item.kind);await expect(page.getByText(`Question ${i+1} of 10`,{exact:true})).toBeVisible();
  if(i===0){await page.getByRole('button',{name:'Get a hint',exact:true}).click();await expect(page.locator('.hint-panel')).toBeVisible();await page.getByRole('button',{name:'Give up',exact:true}).click()}
  else if(item.kind==='mcq'){const p=item.payload;const index=p.options.findIndex((x:any)=>x.id===p.answer_id);await page.locator('.option').nth(index).click();await page.getByRole('button',{name:'Check answer',exact:true}).click()}
  else if(item.kind==='fill_blank'||item.kind==='listening'){await page.getByRole('textbox',{name:'Type your answer'}).fill(item.payload.giveup.answer_display);await page.getByRole('button',{name:'Check answer',exact:true}).click()}
  else if(item.kind==='drag_slot'){const index=item.payload.tiles.findIndex((x:any)=>x.id==='0');await page.locator('.tile').nth(index).click();await page.getByRole('button',{name:'Check answer',exact:true}).click()}
  else if(item.kind==='drag_order'){const p=item.payload;const tiles=p.tiles.filter((x:any)=>!p.distractor_tile_ids.includes(x.id)).sort((a:any,b:any)=>+a.id-+b.id);for(const tile of tiles){const button=page.locator('.tiles').last().getByRole('button',{name:tile.text,exact:true}).first();await button.focus();await page.keyboard.press('Enter')}await page.getByRole('button',{name:'Check answer',exact:true}).click()}
  await expect(page.locator('.feedback')).toBeVisible();if(i===0)await page.locator('.feedback .speak').click();await page.locator('.next-button').click();
 }
 expect(kinds.size).toBeGreaterThan(1);await expect(page.getByRole('heading',{name:'Practice complete.'})).toBeVisible();await expect(page.locator('.summary-stats')).toContainText('10');expect(await page.evaluate(()=>(window as any).__spoken.some((s:any)=>s.lang.startsWith('es')))).toBe(true);
 await page.goto('/dashboard');await expect(page.locator('.dashboard-grid')).toBeVisible();await expect(page.locator('.heatmap>div')).toHaveCount(112);await page.screenshot({path:'../data/dashboard-preview.png',fullPage:true});const overview=await (await page.request.get('/api/stats/overview')).json();expect(overview.total_study_ms).toBeGreaterThan(0);
 await page.goto('/review');await expect(page.locator('tbody tr').first()).toBeVisible();await page.goto('/banks');await page.getByRole('link',{name:'Start test',exact:true}).click();await expect(page.getByRole('button',{name:'Hints are off for this test'})).toBeDisabled();
 for(let i=0;i<40;i++){if(page.url().includes('/summary/'))break;await page.getByRole('button',{name:'Give up',exact:true}).click();await expect(page.locator('.feedback')).toBeVisible();await page.locator('.next-button').click();await page.waitForTimeout(100)}
 await expect(page.getByRole('heading',{name:'Practice complete.'})).toBeVisible();expect(errors).toEqual([]);
});
test('settings persistence and scripted encounter',async({page})=>{
 await page.goto('/settings');await page.getByLabel('Daily goal (minutes)',{exact:true}).fill('20');await page.getByRole('combobox',{name:'Theme'}).selectOption('dark');await page.getByRole('button',{name:'Save settings'}).click();await expect(page.locator('html')).toHaveAttribute('data-theme','dark');await page.reload();await expect(page.getByLabel('Daily goal (minutes)',{exact:true})).toHaveValue('20');
 await page.goto('/encounters');await page.locator('.encounter-card').first().click();await expect(page.locator('.patient-line')).toBeVisible();await page.getByRole('button',{name:'Show English',exact:true}).first().click();await expect(page.locator('.hint-panel')).toBeVisible();await page.getByRole('button',{name:'Give up',exact:true}).click();await expect(page.locator('.feedback')).toBeVisible();
 await page.goto('/settings');await page.getByRole('combobox',{name:'Theme'}).selectOption('light');await page.getByRole('button',{name:'Save settings'}).click();
});
