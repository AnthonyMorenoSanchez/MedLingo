import {test,expect} from '@playwright/test';
test('profile picker creates and isolates learners',async({page})=>{
 await page.goto('/');await expect(page.getByRole('heading',{name:'Welcome to MedLingo'})).toBeVisible();
 await page.getByRole('button',{name:'Create user'}).click();await page.getByLabel('New profile name').fill('Browser learner '+Date.now());await page.getByRole('button',{name:'Create',exact:true}).click();await expect(page.locator('.hero')).toBeVisible();
 const profile=await page.evaluate(()=>localStorage.getItem('medlingo.profile'));expect(profile).not.toBe('1');
 await page.goto('/settings');await page.getByLabel('Daily goal (minutes)',{exact:true}).fill('37');await page.getByRole('button',{name:'Save settings',exact:true}).click();await expect(page.getByText('Settings saved',{exact:true})).toBeVisible();
 await page.getByLabel('Active profile').selectOption('1');await page.waitForURL('/');await page.goto('/settings');await expect(page.getByLabel('Daily goal (minutes)',{exact:true})).not.toHaveValue('37');
 await page.getByLabel('Active profile').selectOption(profile!);await page.waitForURL('/');await page.goto('/settings');await expect(page.getByLabel('Daily goal (minutes)',{exact:true})).toHaveValue('37');
 await page.screenshot({path:'../data/settings-profiles-preview.png',fullPage:true});
});
test('language voices and AI config persist separately',async({page})=>{
 await page.addInitScript(()=>localStorage.setItem('medlingo.profile','1'));await page.goto('/settings');
 await page.getByLabel('Speech source',{exact:true}).nth(0).selectOption('piper');await page.getByLabel('Voice / accent',{exact:true}).nth(0).selectOption('en_US-ryan-medium');
 await page.getByLabel('Speech source',{exact:true}).nth(1).selectOption('piper');await page.getByLabel('Voice / accent',{exact:true}).nth(1).selectOption('es_AR-daniela-high');await page.getByRole('button',{name:'Save settings',exact:true}).click();
 await page.reload();await expect(page.getByLabel('Voice / accent',{exact:true}).nth(0)).toHaveValue('en_US-ryan-medium');await expect(page.getByLabel('Voice / accent',{exact:true}).nth(1)).toHaveValue('es_AR-daniela-high');
 await page.getByLabel('Provider',{exact:true}).selectOption('anthropic');await page.getByLabel('Model name',{exact:true}).fill('example-model');await page.getByLabel('API key',{exact:true}).fill('fake-test-key');await page.getByRole('button',{name:'Save connection',exact:true}).click();await expect(page.getByRole('status')).toContainText('Connection settings saved.');await page.reload();await expect(page.getByLabel('Provider',{exact:true})).toHaveValue('anthropic');await expect(page.getByLabel('API key',{exact:true})).toHaveValue('');
 // Restore offline defaults for the existing study smoke tests.
 await page.getByLabel('Speech source',{exact:true}).nth(0).selectOption('web_speech');await page.getByLabel('Speech source',{exact:true}).nth(1).selectOption('web_speech');await page.getByRole('button',{name:'Save settings',exact:true}).click();
});
test('clinical chat UI sends responses and ends with grading',async({page})=>{
 await page.addInitScript(()=>localStorage.setItem('medlingo.profile','1'));const messages:any[]=[{role:'assistant',content:'Hola, tengo dolor de cabeza.'}];
 await page.route('**/api/ai/conversations',async route=>{if(route.request().method()==='GET')return route.fulfill({json:[]});return route.fulfill({json:{id:999,mode:'clinical',scenario:'Headache',messages,ended:false}})});
 await page.route('**/api/ai/conversations/999/turn',async route=>{const data=route.request().postDataJSON();if(data.text)messages.push({role:'user',content:data.text});messages.push({role:'assistant',content:data.end?'Language score: 82/100. Good use of questions.':'Desde ayer.'});return route.fulfill({json:{id:999,mode:'clinical',scenario:'Headache',messages,ended:!!data.end}})});
 await page.goto('/ai');await page.getByLabel('Mode',{exact:true}).selectOption('clinical');await page.getByRole('button',{name:'Start new conversation'}).click();await expect(page.getByText('Hola, tengo dolor de cabeza.',{exact:true})).toBeVisible();
 await page.getByLabel('Your response',{exact:true}).fill('¿Desde cuándo?');await page.getByRole('button',{name:'Send',exact:true}).click();await expect(page.getByText('Desde ayer.',{exact:true})).toBeVisible();await page.getByRole('button',{name:'End & get feedback'}).click();await expect(page.getByText('Language score: 82/100. Good use of questions.',{exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'Send',exact:true})).toHaveCount(0);await page.screenshot({path:'../data/clinical-preview.png',fullPage:true});
});
