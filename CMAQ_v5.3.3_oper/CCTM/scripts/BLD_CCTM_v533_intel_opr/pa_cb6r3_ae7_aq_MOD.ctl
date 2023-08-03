! for CB6_cl2
IRRTYPE = PARTIAL;
!=======================================================================
! IPR_OUTPUTS
!=======================================================================
!DEFINE FAMILY AOMI  = ALVPO1I+ASVPO1I+ASVPO2I+APOCI+APNCOMI+ALVOO1I+ALVOO2I+ASVOO1I+ASVOO2I;
!DEFINE FAMILY AOMJ  = ALVPO1J+ASVPO1J+ASVPO2J+APOCJ+ASVPO3J+AIVPO1J+APNCOMJ+AISO1J+AISO2J+AISO3J+AMT1J+AMT2J+AMT3J+AMT4J+AMT5J+AMT6J+AMTNO3J+AMTHYDJ+AGLYJ+ASQTJ+AORGCJ+AOLGBJ+AOLGAJ+ALVOO1J+ALVOO2J+ASVOO1J+ASVOO2J+ASVOO3J+APCSOJ+AAVB1J+AAVB2J+AAVB3J+AAVB4J;

DEFINE FAMILY ATOTI = ASO4I+ANO3I+ANH4I+ANAI+ACLI+AECI+AOTHRI+
                      ALVPO1I+ASVPO1I+ASVPO2I+APOCI+APNCOMI+ALVOO1I
                      +ALVOO2I+ASVOO1I+ASVOO2I;

DEFINE FAMILY ATOTJ = ASO4J+ANO3J+ANH4J+ANAJ+ACLJ+AECJ+AOTHRJ+AFEJ+
                      ASIJ+ATIJ+ACAJ+AMGJ+AMNJ+AALJ+AKJ+ALVPO1J+
                      ASVPO1J+ASVPO2J+APOCJ+ASVPO3J+AIVPO1J+APNCOMJ+
                      AISO1J+AISO2J+AISO3J+AMT1J+AMT2J+AMT3J+AMT4J+
                      AMT5J+AMT6J+AMTNO3J+AMTHYDJ+AGLYJ+ASQTJ+AORGCJ+
                      AOLGBJ+AOLGAJ+ALVOO1J+ALVOO2J+ASVOO1J+ASVOO2J+
                      ASVOO3J+APCSOJ+AAVB1J+AAVB2J+AAVB3J+AAVB4J;

DEFINE FAMILY ATOTK = ASOIL+ACORS+ASEACAT+ACLK+ASO4K+ANO3K+ANH4K;

IPR_OUTPUT NO    = HADV + ZADV + HDIF + VDIF + EMIS + DDEP + CLDS + CHEM;

IPR_OUTPUT NO2   = HADV + ZADV + HDIF + VDIF + EMIS + DDEP + CLDS +
                   CHEM        ;

IPR_OUTPUT O3    = HADV + ZADV + HDIF + VDIF +        DDEP + CLDS +
                   CHEM        ;

IPR_OUTPUT ATOTI = HADV + ZADV + HDIF + VDIF + EMIS + DDEP + CLDS +
                   CHEM + AERO;

IPR_OUTPUT ATOTJ = HADV + ZADV + HDIF + VDIF + EMIS + DDEP + CLDS +
                   CHEM + AERO;

IPR_OUTPUT ATOTK = HADV + ZADV + HDIF + VDIF + EMIS + DDEP + CLDS +
                   CHEM + AERO;

!
IRR_OUTPUT NOhuni = <R1> ;
!
IRR_OUTPUT NO2ozNO = <R3> ;
!
IRR_OUTPUT ozoneoodva = <R2> ;
!

ENDPA;