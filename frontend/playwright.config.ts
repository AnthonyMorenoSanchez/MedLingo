import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests/e2e',timeout:90000,workers:1,fullyParallel:false,use:{baseURL:process.env.MEDLINGO_TEST_URL||'http://127.0.0.1:8765',headless:true,viewport:{width:1440,height:1050},screenshot:'only-on-failure'},reporter:[['list'],['json',{outputFile:'test-results/results.json'}]]});
