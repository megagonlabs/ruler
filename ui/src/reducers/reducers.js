import {combineReducers} from 'redux';

import annotations, { highlights, selectedLink, ners } from './annotationsReducer'
import concepts, { selectedConcept } from './conceptsReducer'
import connectivesKeyTypes from           './ConnectivesKeyTypesReducer'
import { label, suggestedLF } from        './labelAndSuggestLFReducer'
import labelClasses from                  './labelClassesReducer'
import labelExamples from                 './labelExampleReducer'
import selectedLF from                    './selectedLFReducer'
import statistics, {statistics_LRmodel} from './statisticsReducer'
import text from                          './textReducer'

const rootReducer = combineReducers({
  annotations,
  concepts,
  gll: connectivesKeyTypes,
  highlights,
  label,
  labelClasses,
  labelExamples,
  ners,
  selectedConcept,
  selectedLF,
  selectedLink,
  suggestedLF,
  statistics,
  statistics_LRmodel,
  text
});

export default rootReducer;

