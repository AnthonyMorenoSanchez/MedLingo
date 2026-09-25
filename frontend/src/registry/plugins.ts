import type {WidgetProps} from '../dashboard/types';
import type {ComponentType} from 'react';
const modules=import.meta.glob('../plugins/**/*.tsx');
export const settingsPanels=new Map<string,ComponentType>();
export async function loadPluginModules(manifests:{modules:string[]}[]){
 for(const manifest of manifests)for(const name of manifest.modules){
  const loader=modules['../plugins/'+name+'.tsx'];if(!loader)continue;
  const module=await loader() as {register?:(api:Record<string,unknown>)=>Promise<void>|void};
  if(module.register)await module.register({
   registerQuestionType:async(id:string,component:ComponentType)=>{const {questionTypes}=await import('./questionTypes');Object.assign(questionTypes,{[id]:component})},
   registerWidget:async(id:string,component:ComponentType<WidgetProps>,span=6)=>{const {dashboardWidgets}=await import('./dashboardWidgets');dashboardWidgets.push({id,component,span})},
   registerSettingsPanel:(id:string,component:ComponentType)=>settingsPanels.set(id,component)
  });
 }
}
