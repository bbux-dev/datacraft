# Concrete Examples

## Generating Sentences to Train a Classifier On
When training a Machine Learning Classifier, it can be difficult to create labeled data from scratch.  By analyzing the structure
of the data it may be possible to augment the small initial set of examples by generating additional similar data that follows
the same structure. For example, we want to create an Insult detector. Let's say these are the initial examples we have:

```
1,You are such a schmuck
1,You're a complete and utter moron
1,You're so stupid
1,You're an idiot
0,You are such a blessing
0,You're a complete and utter help
0,You're so cute
0,You're an insperation
```

By examining these sentences we can get an idea of the general structure of an insult.  We might break it down like this.

```
PRONOUN_IDENTIFIER ADVERB_MODIFIER ADJECTIVE_INSULT
      You are           so             stupid

PRONOUN_IDENTIFIER DETERMINANT NOUN_INSULT
      You're            an        idiot
```

To generate more sample sentences, we would just need to fill in examples for each of the identified parts.  Our spec might
look like:

```json
{
  "insults1": {
    "type": "combine",
    "refs": ["PRONOUN_IDENTIFIER", "ADVERB_MODIFIER", "ADJECTIVE_INSULT"],
    "config": { "join_with": " ", "prefix": "1,"}
  },
  "insults2": {
    "type": "combine",
    "refs": ["PRONOUN_IDENTIFIER", "DETERMINANT", "NOUN_INSULT"],
    "config": { "join_with": " ", "prefix": "1,"}
  },
  "compliments1": {
    "type": "combine",
    "refs": ["PRONOUN_IDENTIFIER", "ADVERB_MODIFIER", "ADJECTIVE_COMPLIMENT"],
    "config": { "join_with": " ", "prefix": "0,"}
  },
  "compliments2": {
    "type": "combine",
    "refs": ["PRONOUN_IDENTIFIER", "DETERMINANT", "NOUN_COMPLIMENT"],
    "config": { "join_with": " ", "prefix": "0,"}
  },
  "refs":{
    "PRONOUN_IDENTIFIER": ["You are", "You're"],
    "ADVERB_MODIFIER": ["so", "extremely", "utterly", "incredibly"],
    "DETERMINANT": {"a":  0.3, "an": 0.3, "such a": 0.3, "a complete and utter": 0.1},
    "ADJECTIVE_INSULT": ["stupid", "dumb", "idiotic", "imbecilic", "useless", "ugly"],
    "NOUN_INSULT": ["idiot", "schmuck", "moron", "imbecile", "poop face"],
    "ADJECTIVE_COMPLIMENT": ["nice", "sweet", "kind", "smart"],
    "NOUN_COMPLIMENT": ["inspiration", "blessing", "friend"]
  }
}
```

Looking at some of the insults produced
```shell script
dist/datamaker -s ~/scratch/insults.json -i 100 | grep '1,' | tail
1,You're incredibly ugly
1,You're a idiot
1,You are so stupid
1,You are an schmuck
1,You're extremely dumb
1,You're an moron
1,You are utterly idiotic
1,You are a imbecile
1,You're incredibly imbecilic
1,You're a poop face
```

This is toy example and there are lots of issues with it, but this did give us another 100 or so examples to work with.
Until we are able to get access to better data, this can be used to boot strap the process.
